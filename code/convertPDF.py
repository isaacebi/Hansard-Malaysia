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

# %%
PARENT_PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
DATA_PATH = os.path.join(PARENT_PATH, 'data')
PDF = os.path.join(DATA_PATH, 'PDF')
TEST = os.path.join(PDF, 'hansard_14-03-k01-01.pdf')
TEXT = os.path.join(DATA_PATH, 'TEXT')
COMPILE_TEXT = os.path.join(TEXT, 'compile.txt')

# %%
# for head, body, file in os.walk(PDF):
#     print(file)

# %%
# check or create path
isExist(TEXT)

with open(COMPILE_TEXT, 'w') as f:

    #create file object variable
    pdffileobj=open(TEST,'rb')
    
    #create reader variable that will read the pdffileobj
    pdfreader=PyPDF2.PdfFileReader(pdffileobj)
    
    #This will store the number of pages of this pdf file
    x=pdfreader.numPages
    
    #create a variable that will select the selected number of pages
    pageobj=pdfreader.getPage(x+1)
    
    #(x+1) because python indentation starts with 0.
    #create text variable which will store all text datafrom pdf file
    text=pageobj.extractText()

    f.writelines(text)

# %%