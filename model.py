from WordSegmentation import wordSegmentation, prepareImg
import os
from PIL import Image
import pytesseract
import cv2
from LinesSegmentation import lineSegmentation
import matplotlib.pyplot as plt


def predict(filePath):
    pytesseract.pytesseract.tesseract_cmd = r'C:\api_model\Site_back\Tesseract-OCR\tesseract.exe'
    img = cv2.imread(filePath)
    tmp_line = lineSegmentation(img)
    text = []
    i = 0
    for line in tmp_line:
        imgLine = prepareImg(line, 50)
        tmp_words = wordSegmentation(imgLine, kernelSize=25, sigma=11, theta=7, minArea=200)
        for word in tmp_words:
            exmp = Image.open(filePath)
            text.append(pytesseract.image_to_string(exmp, lang='rus'))
            i += 1
    return text

