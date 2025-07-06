import re
import os
import json
from datetime import datetime

from config import DATABASE_FILE

# Check if the json database file exists and is not empty, otherwise return an empty list as new database
# TODO: Consider circumstances where some signposting is necessary here...
def load_database():
    if os.path.exists(DATABASE_FILE) and os.path.getsize(DATABASE_FILE) > 0:
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            try: 
                return json.load(f)
            except json.JSONDecodeError: 
                return []
    return []

def add_items_to_database(new_items: list):
    # Saves finalized items to json database, returns if nothing to save
    if not new_items: 
        return
    database = load_database()
    receipt_date = datetime.now().strftime("%Y-%m-%d")
    for item in new_items:
        database.append({
            "date": receipt_date,
            "item_name": item.get('name'),
            "total_price": item.get('total_price'),
        })
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=4, ensure_ascii=False)
    print(f"\n[SUCCESS] Successfully added {len(new_items)} items to the database.")

def finalize_item_data(item_data: dict) -> dict:
    # Cleans parsed data
    finalized = {}
    finalized['name'] = str(item_data.get('name', 'N/A')).strip()
    
    # Clean the total_price
    raw_price = str(item_data.get('total_price', '0') or '0')
    standardized_price = raw_price.replace(',', '.')
    cleaned_price = re.sub(r'[^\d.]', '', standardized_price)
    try:
        finalized['total_price'] = float(cleaned_price) if cleaned_price else 0.0
    except (ValueError, TypeError):
        finalized['total_price'] = 0.0
    
    # Keep the original line for context during editing in review
    if 'original_line' in item_data:
        finalized['original_line'] = item_data['original_line']

    return finalized