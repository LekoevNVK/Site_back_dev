from model import OCR
import os

print(OCR.predict(os.curdir + f'\text\txt8.png'))