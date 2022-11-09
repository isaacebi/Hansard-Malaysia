# %%
import os
import numpy as np
import pandas as pd
import pathlib
import re
import zipfile
import shutil
import PyPDF2
from pdfminer.high_level import extract_text
from tqdm import tqdm
import fitz

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

            # by logic start should be less than end
            if startPage and endPage:
                break
            else:
                continue

    page = extract_text(TEST, page_numbers=[x for x in range(startPage, endPage+1)])
    page = ' '.join(page.split())

    patterns = ['YAB.*?\)', 'YB.*?\)']

    yang_hadir = []
    for pattern in patterns:
        hadir = re.findall(pattern, page)
        yang_hadir += hadir

    for i, hadir in enumerate(yang_hadir):
        hadir = re.sub('YB.', '', hadir)
        hadir = re.sub('YAB.', '', hadir)
        #hadir = re.sub(r'[()]', '', hadir) # remove brackets
        # get name of MP
        peopleHadir = hadir.split('(')[0]
        peopleHadir = ' '.join(peopleHadir.split()) # cleaning
        # get seat of MP
        seatHadir = hadir.split('(')[1]
        seatHadir = re.sub(r'[()]', '', seatHadir) # cleaning
        # for dataframe format
        getHadir = {
            'MP': peopleHadir,
            'seat': seatHadir
        }
        yang_hadir[i] = getHadir

    return pd.DataFrame(yang_hadir)

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

TEST = os.path.join(PDF, 'hansard_14-03-k01-01.pdf')
# %%
ahliDewan2 = pd.read_csv(AHLI_DEWAN2)

# %%
def extractByName(page, hadir, pdf_page, pdfDate):
    # create emtpy list
    allDialog = []
    # load page
    text = page.get_text('xhtml')

    # remove inline
    text = " ".join(text.split())
    
    # using name as start
    for i in range(len(hadir)):
        pattern = f"{hadir['MP'][i]} \[{hadir['seat'][i]}].*?\<p><b>"
        matches = re.findall(pattern, text, flags=re.IGNORECASE)

        # extract into dictonary
        for match in matches:
            # remove html format
            patterns = ['</b>', '<b>', '</p>', '<p>', '</i>', '<i>']
            for pattern in patterns:
                match = re.sub(pattern, '', match)     

            # to dict
            dialog = {
                'MP': name,
                'dialog': match,
                'pdf_page': pdf_page,
                'pdf_date': pdfDate
            }
            allDialog.append(dialog)
    
    return pd.DataFrame(allDialog)

def extractSession(page):
    # load page
    text = page.get_text('xhtml')

    # get pdf date
    if pdf_page == 10:
        pattern = 'DR.*?\d{4}\s'
        pdfDate = re.findall(pattern, text)
        pdfDate = "".join(pdfDate[0].split())
        return pdfDate

    else:
        return False

# %%
# emtpy dataframe
allDialog = pd.DataFrame()
for root, dirs, files in os.walk(PDF):
    for name in tqdm(files):
        # get file path
        file = os.path.join(root, name)
        # read pdf
        pdf = fitz.open(file)

        # input: fileName, fileName path
        dfHadir = mpHadir(pdf, PDF)

        # iterate over page - get date
        for pdf_page, page in enumerate(pdf):
            pdfDate = extractSession(page)
            # if get pdfDate then break
            if pdfDate:
                break
            else:
                continue

        # iterate over page - get dialog
        for pdf_page, page in enumerate(pdf):
            pdf_page += 1 # since python index start 0
            dfDialogPage = extractByName(page, dfHadir, pdf_page, pdfDate)
            allDialog = pd.concat([allDialog, dfDialogPage], ignore_index=True)

# here
# %%
allDialog['MP'] = allDialog['dialog'].apply(lambda x: x.split('[')[0])
allDialog['seat'] = allDialog['dialog'].apply(lambda x: x.split('[')[1].split(']')[0])
allDialog['dialog'] = allDialog['dialog'].apply(lambda x: x.split(']')[1])

# %%
allDialog
# %%
