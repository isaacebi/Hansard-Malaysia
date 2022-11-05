# %%
import PyPDF2
import os
import pandas as pd
import numpy as np

# %%
def isExist(checkPath):
    isExist = os.path.exists(checkPath)
    if not isExist:
        os.mkdir(checkPath)

def toPDF(filePath, toWrite):
    with open(filePath, 'rb') as reader:
        # create reader variable that will read the pdffileobj
        pdfreader=PyPDF2.PdfFileReader(reader, strict=False)

        # get total pages
        totalPages = pdfreader.numPages

        for curPages in range(totalPages):
            pageObj = pdfreader.getPage(curPages)
            text = pageObj.extractText()
            toWrite.writelines(text)

# %%
PARENT_PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
DATA_PATH = os.path.join(PARENT_PATH, 'data')
PDF = os.path.join(DATA_PATH, 'PDF')
TEXT = os.path.join(DATA_PATH, 'TEXT')
COMPILE_TEXT = os.path.join(TEXT, 'compile.txt')

# %%
# check or create path
isExist(TEXT)

with open(COMPILE_TEXT, 'w', encoding='utf-8') as f:
    for head, body, files in os.walk(PDF):
        for file in files:
            file = os.path.join(head, file)
            toPDF(file, f)

# %%