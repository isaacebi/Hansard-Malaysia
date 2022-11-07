# %%
from pdf2image import convert_from_path
import os
import pandas as pd
import numpy as np
import pytesseract
import shutil
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

# %%
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

# %%
def isExist(checkPath):
    isExist = os.path.exists(checkPath)
    if not isExist:
        os.mkdir(checkPath)

def pdfToImage(filePath, IMAGE_PATH):
    fileName = os.path.basename(filePath)
    pages = convert_from_path(filePath)
    for i in range(len(pages)):
        pageName = f'page_{i+1}.jpg'
        path_ = os.path.join(IMAGE_PATH, pageName)
        pages[i].save(path_, 'JPEG')      

def getText(main_dir, fileName, folderName):
    fileOpen = os.path.join(main_dir, fileName)
    text = pytesseract.image_to_string(Image.open(fileOpen))
    
    eaPageName = os.path.join(folderName, f'{fileName}.txt')

    # get text each pdf page
    with open(eaPageName, 'w') as f:
        f.write(text)              

# %%
PARENT_PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
DATA_PATH = os.path.join(PARENT_PATH, 'data')
PDF = os.path.join(DATA_PATH, 'PDF')
TEXT = os.path.join(DATA_PATH, 'TEXT')
GET_TEXT = os.path.join(DATA_PATH, 'GET_TEXT')
IMAGE = os.path.join(DATA_PATH, 'IMAGE')
COMPILE_TEXT = os.path.join(TEXT, 'compile.txt')
AHLI_DEWAN2 = os.path.join(DATA_PATH, 'ahliDewan2.csv')

TEST = os.path.join(PDF, 'hansard_14-03-k01-01.pdf')

# # %%
# check or create path
isExist(TEXT)
isExist(GET_TEXT)

# PDF folder
for head, body, files in os.walk(PDF):
    for file in files:
        # create temp image folder
        isExist(IMAGE)
        file = os.path.join(head, file)
        pdfToImage(file, IMAGE)

        # IMAGE folder
        # too slow - https://yasoob.me/2019/05/29/speeding-up-python-code-using-multithreading/
        for headImage, bodyImage, filesImage in os.walk(IMAGE):
            for fileImage in filesImage:
                # naming folder for each pdf
                pdfName = os.path.basename(file)
                eaFolderName = os.path.join(GET_TEXT, f'{pdfName[:-4]}')
                
                # avoid repeated PDF
                checkExist = os.path.exists(eaFolderName)
                if not checkExist:
                    getText(headImage, fileImage, eaFolderName)
                    # fileOpen = os.path.join(headImage, fileImage)
                    # text = pytesseract.image_to_string(Image.open(fileOpen))
                    
                    # eaPageName = os.path.join(eaFolderName, f'{fileImage}.txt')

                    # # get text each pdf page
                    # with open(eaPageName, 'w') as f:
                    #     f.write(text)

        # delete temp image folder
        print('pass')
#         shutil.rmtree(IMAGE)        

# %%
