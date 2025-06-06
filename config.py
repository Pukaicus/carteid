import os
import pytesseract

# Configuration Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\tesseract\tesseract.exe'
os.environ["TESSDATA_PREFIX"] = r"C:\tesseract\tessdata"
POPPLER_PATH = r'C:\poppler\poppler-24.08.0\Library\bin'

# Dossiers
INPUT_FOLDER = r'D:\carteid_cv'
OUTPUT_FOLDER = os.path.join(INPUT_FOLDER, 'xml')
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
