import os
import sys
import pytesseract

from parser import parse_receipt_data
from cli_handler import review_and_correct_items
from data_manager import add_items_to_database
from image_processing import preprocess_image
from correction_manager import apply_memory

from config import IMAGE_TO_TEST, TESSERACT_CONFIG, LOGS_DIR

def main():
    try:
        # Check if debugging directory exists, create if not
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)

        print("\n   I. Preprocessing image with OpenCV")
        processed_image = preprocess_image(IMAGE_TO_TEST)
        if processed_image is None: 
            return

        print("\n   II Extracting text with Tesseract")
        raw_text = pytesseract.image_to_string(processed_image, lang='est', config=TESSERACT_CONFIG)
        print("Raw OCR Text:\n" + raw_text)

        print("\n   III Parsing and applying memory")
        raw_items = parse_receipt_data(raw_text)
        initial_items = apply_memory(raw_items)

        # Check if any items were parsed
        if not initial_items:
            print("\n[ERROR] No items could be parsed from the image.")
            return

        print("\n   IV Interactive review and correction")
        final_items = review_and_correct_items(initial_items)

        if not final_items:
            print("\n[INFO] No items were finalized for the database.")
            return

        print("\n   V Finalizing and Saving to Database")
        add_items_to_database(final_items)

        print("\n[SUCCESS] Processing complete!")

    except KeyboardInterrupt:
        print("\n\n[INFO] Operation cancelled by user. No data was saved.")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

if __name__ == "__main__":
    main()