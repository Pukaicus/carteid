import os
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
from config import POPPLER_PATH

def ocr_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.pdf':
        pages = convert_from_path(filepath, poppler_path=POPPLER_PATH)
        text = ""
        for page in pages:
            text += pytesseract.image_to_string(page, lang='fra') + "\n"
        return text
    else:
        img = Image.open(filepath)
        return pytesseract.image_to_string(img, lang='fra')
