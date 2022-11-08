# %%
import os
import numpy as np
import pandas as pd
import pathlib
import re
import zipfile
import shutil

# %%
# helper function
def spaceDash(text):
    storeKey = re.findall('( \-\w+)', text)
    for match in storeKey:
        text = re.sub(match, match.strip(), text)
    return text

# def dialogExtractor(text, ahliDewan, pdfSession, pageNumber):
#     listDialog = []

#     speaker = ahliDewan.Nama.tolist()
#     speaker += [
#         'Tuan Yang di-Pertua', 'Beberapa Ahli', 'Timbalan Menteri Dalam Negeri |'
#         ]

#     for namaTarget in speaker:
#         text = re.sub(namaTarget, '#namaTarget', text)

#     for seat in ahliDewan.Kawasan:
#         pattern = '\[' + seat + '.*?\#namaTarget'
#         matches = re.findall(pattern, text, flags=re.IGNORECASE)

#         for match in matches:
#             dialog = {
#                 'dialog': match,
#                 'pdf_session': pdfSession,
#                 'page_number': pageNumber        
#             }
#             listDialog.append(dialog)
#     return listDialog

def dialogExtractor(text, ahliDewan, pdfSession, pageNumber):
    listDialog = []

    for seat in ahliDewan.Kawasan:
        pattern = '\[' + seat + '\]:.*?\:'
        matches = re.findall(pattern, text, flags=re.IGNORECASE)

        # need new logic for faster execution
        for match in matches:
            dialog = {
                'dialog': match,
                'pdf_session': pdfSession,
                'page_number': pageNumber        
            }
            listDialog.append(dialog)
    return listDialog

def removeExtra(text, ahliDewan):
    for i in range(len(ahliDewan)):
        kawasan = ahliDewan.Kawasan[i]
        nama = ahliDewan.Nama[i]
        pattern = f"{nama}.*?\[{kawasan}\]:.+"
        text = re.sub(pattern, '', text)
        
        # special case
        sPattern = ['Tuan Yang di-Pertua:', 'YM Datuk Seri Utama Tengku Zafrul Tengku Abdul Aziz]:']
        for pattern in sPattern:
            text = re.sub(pattern, '', text)

    return text

# get name MP hadir
def mpHadir(fileName, pdfPath):
    filePath = os.path.join(pdfPath, f'{fileName}.pdf')
    pdf_active = PyPDF2.PdfFileReader(open(TEST, 'rb', ),strict=False)

    numPages = pdf_active.numPages

    for i in range(numPages):
        curPage = ''.join(pdf_active.getPage(i).extractText().split()).lower()
        if 'senaraikehadiran' in curPage or 'ahliyanghadir' in curPage:
            startPage = i
        if 'yangtidakhadir' in curPage: 
            endPage = i
        if startPage and endPage:
            break
        else:
            continue

    page = extract_text(TEST, page_numbers=[x for x in range(startPage, endPage+1)])
    page = ' '.join(page.split())

    patterns = ['YAB.*?\(', 'YB.*?\(']

    yang_hadir = []
    for pattern in patterns:
        hadir = re.findall(pattern, page)
        yang_hadir += hadir

    for i, hadir in enumerate(yang_hadir):
        hadir = re.sub('YB.', '', hadir)
        hadir = re.sub('YAB.', '', hadir)
        hadir = re.sub(r'[()]', '', hadir)
        hadir = ' '.join(hadir.split())
        yang_hadir[i] = hadir

    return yang_hadir

# %%
# pathing
PARENT_PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
DATA_PATH = os.path.join(PARENT_PATH, 'data')
PDF = os.path.join(DATA_PATH, 'PDF')
TEXT = os.path.join(DATA_PATH, 'TEXT')
COMPILE_TEXT = os.path.join(TEXT, 'compile.txt')
DIALOG = os.path.join(TEXT, 'compileDialog.txt')
AHLI_DEWAN2 = os.path.join(DATA_PATH, 'ahliDewan2.csv')
ZIP = os.path.join(DATA_PATH, 'GET_TEXT.zip')
GET_TEXT = os.path.join(DATA_PATH, 'GET_TEXT') # only exist after zip

# %%
ahliDewan2 = pd.read_csv(AHLI_DEWAN2)

# %%
isExist = os.path.exists(GET_TEXT)
if not isExist:
    with zipfile.ZipFile(ZIP, 'r') as zip_ref:
        zip_ref.extractall(DATA_PATH)

# %%
shutil.rmtree(GET_TEXT)

# %%
dialog_DF = pd.DataFrame()
for root, dirs, files in os.walk(GET_TEXT):
    for name in files:
        # get file path
        file = os.path.join(root, name)

        # get page number
        page = name[:-8]

        # get pdf session
        pdf = os.path.basename(root)

        # mp hadir
        listHadir = mpHadir(pdf, PDF) ### use name and try else

        # for python 3.5 or later
        txt = pathlib.Path(file).read_text()

        # remove extra inline
        txt = txt.replace('\n', '')

        # remove extra space
        txt = " ".join(txt.split())

        # remove space + dash O(regexMatch) compute time
        txt = spaceDash(txt)

        # extract dialog each MP
        listDialog = dialogExtractor(txt, ahliDewan2, pdf, page)
        listDialog = pd.DataFrame(listDialog)
        dialog_DF = pd.concat([dialog_DF, listDialog], ignore_index=True)

# %%
dialog_DF['page_number'] = dialog_DF.page_number.str.extract('(\d+)', expand=True)
# dialog_DF['dialog'] = dialog_DF.dialog.apply(lambda x: removeExtra(x, ahliDewan2))


dialog_DF.to_csv('test.csv', index=False)

# %%
TEST = os.path.join(PDF, 'hansard_14-03-k01-01.pdf')

import PyPDF2
from pdfminer.high_level import extract_text





# %%
