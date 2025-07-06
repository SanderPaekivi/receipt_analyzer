import os
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = 'data'
RECEIPTS_DIR = os.path.join(DATA_DIR, 'receipts')
LOGS_DIR = 'logs' # For debug images

IMAGE_TO_TEST = os.path.join(RECEIPTS_DIR, "test4.jpg") 

OCR_MEMORY_FILE = os.path.join(DATA_DIR, 'ocr_memory.json')
DATABASE_FILE = os.path.join(DATA_DIR, 'database.json')

TESSERACT_CONFIG = '--psm 4'