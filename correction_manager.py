# correction_manager.py

import json
import os
from fuzzywuzzy import process
from config import OCR_MEMORY_FILE

def load_memory():
    # Loads the OCR memory file, with learned corrections and dismissals
    if os.path.exists(OCR_MEMORY_FILE) and os.path.getsize(OCR_MEMORY_FILE) > 0:
        with open(OCR_MEMORY_FILE, 'r', encoding='utf-8') as f:
            try: 
                return json.load(f)
            except json.JSONDecodeError: 
                pass
    return {"corrections": {}, "dismissals": []}

def save_memory(memory_data):
    # Saves memory back to the JSON file
    with open(OCR_MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory_data, f, indent=4, ensure_ascii=False)

def apply_memory(items: list) -> list:
    # Applies learned corrections and dismissals to a list of parsed items
    # Prioritizes exact matches before attempting a fuzzy search, to deal with strange edge cases like commas and quotation marks
    memory = load_memory()
    corrections = memory.get('corrections', {})
    dismissals = memory.get('dismissals', [])
    
    processed_items = []
    for item in items:
        original_name = item.get('name', '')
        if not original_name: # Skip if the name is empty
            processed_items.append(item)
            continue
        # TODO: Check fuzzy match threshold scores, perhaps make configurable or variable or ... something, to be sure!
        # Checking for dismissables via exact match 
        if original_name in dismissals:
            item['status'] = 'dismissed'
            print(f"[INFO] Auto-dismissing '{original_name}' (exact match found)")
            processed_items.append(item)
            continue
        
        # If no exact match, trying a FUZZY match
        elif dismissals:
            best_dismiss_match, score = process.extractOne(original_name, dismissals)
            if score > 90:
                item['status'] = 'dismissed'
                print(f"[INFO] Auto-dismissing '{original_name}' (similar to '{best_dismiss_match}')")
                processed_items.append(item)
                continue

        # Checking for corrections via exact match first
        if original_name in corrections:
            item['name'] = corrections[original_name]
            item['status'] = 'corrected'
        # If no exact match, trying a FUZZY match
        elif corrections:
            best_correct_match, score = process.extractOne(original_name, corrections.keys())
            if score > 88: 
                item['name'] = corrections[best_correct_match]
                item['status'] = 'corrected'
                print(f"[INFO] Auto-correcting '{original_name}' to '{item['name']}' (similar to '{best_correct_match}')")
        
        processed_items.append(item)
        
    return processed_items

def learn_correction(original_name: str, corrected_name: str):
    # Saves a new name correction to memory
    if not original_name or not corrected_name or original_name == corrected_name:
        return
    memory = load_memory()
    memory['corrections'][original_name] = corrected_name
    save_memory(memory)
    print(f"[INFO] Learned new correction: '{original_name}' -> '{corrected_name}'")

def learn_dismissal(dismissed_item_name: str):
    # Saves a new dismissal pattern to memory
    if not dismissed_item_name:
        return
    memory = load_memory()
    if dismissed_item_name not in memory['dismissals']:
        memory['dismissals'].append(dismissed_item_name)
        save_memory(memory)
        print(f"[INFO] Learned to dismiss lines like: '{dismissed_item_name}'")