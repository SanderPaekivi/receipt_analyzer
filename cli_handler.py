# cli_handler.py

from data_manager import finalize_item_data
from correction_manager import learn_correction, learn_dismissal
import math

def review_and_correct_items(items: list) -> list:
    # Table view with pagination for confirming, editing, and dismissing items found from raw OCR
    dismissal_tags = set()
    
    # Pagination state
    page_size = 15
    current_page = 0

    while True:
        # Pagination calculations
        total_pages = math.ceil(len(items) / page_size)
        total_pages = max(1, total_pages) # Ensures at least 1 page
        start_index = current_page * page_size
        end_index = start_index + page_size
        page_items = items[start_index:end_index]

        print("\n Parsed Items Review")
        print(f"--- Page {current_page + 1} / {total_pages} ---")
        print(f"{'ID':<4} | {'Status':<12} | {'Item Name':<40} | {'Total Price':<12}")
        print("-" * 78)
        
        # Enumerating from global start_index for consistent IDs
        for item_index, item in enumerate(page_items, start=start_index):
            status = item.get('status', 'parsed').upper() # Default status is 'parsed', others are given by either past memory or editing. 
            if item_index in dismissal_tags:
                status = '[DEL]'

            name_str = item.get('name', 'N/A')
            total_p_val = item.get('total_price')
            total_p_str = f"{total_p_val:.2f}" if isinstance(total_p_val, (int, float)) else "N/A"

            print(f"{item_index:<4} | {status:<12} | {name_str:<40} | {total_p_str:<12}")
        
        print("\n[INPUT] [Enter] to Accept | [e <ID>] to Edit | [d <IDs...>] to Dismiss | [n]ext | [p]revious")
        action = input("Your choice: ").lower().split()

        if not action: break 

        cmd = action[0]
        args = action[1:]

        # Navigation commands
        if cmd == 'n':
            if current_page < total_pages - 1:
                current_page += 1
            else:
                print("[INFO] Already on the last page.")
            continue
        
        if cmd == 'p':
            if current_page > 0:
                current_page -= 1
            else:
                print("[INFO] Already on the first page.")
            continue

        if cmd == 'e' and len(args) == 1 and args[0].isdigit():
            idx = int(args[0])
            if 0 <= idx < len(items):
                items[idx] = _get_manual_entry(items[idx])
            else:
                print("[ERROR] Invalid item number for editing.")

        elif cmd == 'd' and args:
            for arg in args:
                if arg.isdigit():
                    idx = int(arg)
                    if 0 <= idx < len(items):
                        if idx in dismissal_tags:
                            dismissal_tags.remove(idx)
                        else:
                            dismissal_tags.add(idx)
                    else:
                        print(f"[ERROR] Invalid item number for dismissal: {idx}")
        else:
            print("[ERROR] Unrecognized command.")

    final_items = []
    for item_index, item in enumerate(items):
        if item_index in dismissal_tags:
            learn_dismissal(item.get('name'))
        else:
            final_items.append(item)
            
    return final_items

def _get_manual_entry(original_item: dict) -> dict:
    # Helper function for manual data entry (name and price)
    print("-" * 20)
    print(f"Editing Item (Original: '{original_item.get('original_line', '')}')")
    
    name_prompt = original_item.get('name', '')
    total_p_prompt = original_item.get('total_price', '')

    name = input(f"  - Name [{name_prompt}]: ") or name_prompt
    total_p = input(f"  - Total Price [{total_p_prompt}]: ") or str(total_p_prompt)

    learn_correction(original_item.get('name'), name)

    return finalize_item_data({
        "name": name,
        "total_price": total_p,
        "original_line": original_item.get('original_line')
    })