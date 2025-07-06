import re
from data_manager import finalize_item_data 

def parse_receipt_data(raw_text: str) -> list:
    # Parses raw OCR text by finding the last price-like element on each line (numeric + decimal separator + numeric)
    # Everything to the left of the last price is considered as name-like
    parsed_items = []
    
    # Regex for one or more digits, followed by a separator (comma or period), followed by exactly two digits (handles spaces around the separator)
    price_pattern = re.compile(r'(\d+[\s,.]+\d{2})')

    print("\n[INFO] Parsing receipt using simple price-detection logic...")

    # Loop through lines of Tesseract output
    for line in raw_text.split('\n'):
        line = line.strip()
        if not line:
            continue

        # Find all occurrences of price pattern on current line
        matches = price_pattern.findall(line)

        # If no price-like pattern was found on this line, skip 
        if not matches:
            print(f"[DEBUG] No price found in: '{line}'")
            continue

        # Actual price is the LAST match found on the line
        last_price_str = matches[-1]

        # Split the line from the right once,price as the separator
        parts = line.rsplit(last_price_str, 1)
        item_name = parts[0].strip()

        print(f"[DEBUG] Match found! Name: '{item_name}', Price: '{last_price_str}'")

        # Creating dictionary with extracted data
        item_data = {
            'name': item_name,
            'total_price': last_price_str,
            'original_line': line
        }

        # Clean  data and add it to our list
        parsed_items.append(finalize_item_data(item_data))
            
    return parsed_items