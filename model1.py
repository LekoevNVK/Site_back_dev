from PIL import Image
import os
import pytesseract


def predict(filePath):
    pytesseract.pytesseract.tesseract_cmd = r'C:\api_model\Site_back\Tesseract-OCR\tesseract.exe'
    exmp = Image.open(filePath)
    return pytesseract.image_to_string(exmp, lang='rus')
