# %%
import os
import numpy as np
import pandas as pd
import pathlib
import re

# %%
# helper function
def spaceDash(text):
    storeKey = re.findall('( \-\w+)', text)
    for match in storeKey:
        text = re.sub(match, match.strip(), text)
    return text

# %%
# pathing
PARENT_PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
DATA_PATH = os.path.join(PARENT_PATH, 'data')
PDF = os.path.join(DATA_PATH, 'PDF')
TEXT = os.path.join(DATA_PATH, 'TEXT')
COMPILE_TEXT = os.path.join(TEXT, 'compile.txt')
DIALOG = os.path.join(TEXT, 'compileDialog.txt')
AHLI_DEWAN2 = os.path.join(DATA_PATH, 'ahliDewan2.csv')

# %%
# for python 3.5 or later
txt = pathlib.Path(COMPILE_TEXT).read_text(encoding='utf-8')

# remove extra inline
txt = txt.replace('\n', '')

# remove extra space
txt = " ".join(txt.split())

# marker stop page
txt = txt.replace('PENERANGAN DARIPADA MENTERI -MENTERI', 'pageStop')

# marker start page
txt = re.sub('(Bil. \d)', 'pageStart', txt)

# remove marked page
txt = re.sub('pageStart.+?pageStop', '', txt)

# %%
# remove space + dash O(regexMatch) compute time
txt = spaceDash(txt)

# %%
# check point
with open(DIALOG, 'w', encoding='utf-8') as f:
    f.write(txt)

# %%
ahliDewan2 = pd.read_csv(AHLI_DEWAN2)

# %%
def dialogExtractor(text, ahliDewan):
    listDialog = []

    for namaTarget in ahliDewan.Nama:
        text = re.sub(namaTarget, '#namaTarget', text)

    for seat in ahliDewan.Kawasan:
        pattern = '\[' + seat + '.*?\#namaTarget'
        matches = re.findall(pattern, text, flags=re.IGNORECASE)

        for match in matches:
            dialog = {
                'dialog': match               
            }
            listDialog.append(dialog)
    return listDialog

listDialog = dialogExtractor(txt, ahliDewan2)

# %%
listDialog = pd.DataFrame(listDialog)

# %%
