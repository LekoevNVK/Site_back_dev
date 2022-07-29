from scr.WordSegmentation import wordSegmentation, prepareImg
import os
from PIL import Image
import cv2
from scr.LinesSegmentation import lineSegmentation
import matplotlib.pyplot as plt
import torch
import glob

from scr.config import MODEL, BATCH_SIZE, N_HEADS, \
    ENC_LAYERS, DEC_LAYERS, LR, \
    DEVICE, RANDOM_SEED, HIDDEN, \
    DROPOUT, CHECKPOINT_FREQ, N_EPOCHS, \
    ALPHABET, TRAIN_TRANSFORMS, TEST_TRANSFORMS, \
    OPTIMIZER_NAME, SCHUDULER_ON, PATIENCE
from scr.utils import generate_data, process_data, prediction
from pathlib import Path
from scr.models.model2 import TransformerModel


class OCR:
    def predict(filePath, wordIS):
        char2idx = {char: idx for idx, char in enumerate(ALPHABET)}
        idx2char = {idx: char for idx, char in enumerate(ALPHABET)}

        model = TransformerModel(len(ALPHABET), hidden=HIDDEN, enc_layers=ENC_LAYERS, dec_layers=DEC_LAYERS,
                                 nhead=N_HEADS, dropout=DROPOUT).to(DEVICE)
        model.load_state_dict(torch.load("checkpoint_131.pt", map_location='cpu'))
        img = cv2.imread(os.curdir + filePath)
        if wordIS == 'слово':
            plt.imsave(os.curdir + f'\word\txt0.png', img)
            prdct = prediction(model, Path(Path.cwd(), 'word'), char2idx, idx2char)
            files = glob.glob('word/')
            for f in files: os.remove(f)
            return ' '.join(prdct.values())
        tmp_line = lineSegmentation(img)
        i = 0
        for line in tmp_line:
            imgLine = prepareImg(line, 50)
            tmp_words = wordSegmentation(imgLine, kernelSize=25, sigma=11, theta=7, minArea=200)
            for word in tmp_words:
                plt.imsave(os.curdir + f'\word\txt{i}.png', word[1])
                i += 1
        prdct = prediction(model, Path(Path.cwd(), 'word'), char2idx, idx2char)
        files = glob.glob('word/')
        for f in files: os.remove(f)
        return ' '.join(prdct.values())