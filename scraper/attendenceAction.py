# %%
from urllib.error import URLError
import urllib.request
import pandas as pd
import numpy as np
import time
import os
from datetime import date
import PyPDF2
from pdfminer.high_level import extract_text

# %% helper function
def below_avg(row):
    color = 'white'

    if row.total < 72:
        color = 'red'

    return ['background-color: %s' % color]*len(row.values)

# %%
PARENT_PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
DATA_PATH = os.path.join(PARENT_PATH, 'data')
MP_PATH = "https://raw.githubusercontent.com/isaacebi/Hansard-Malaysia/main/data/mp_2022-10-10.csv"
SESSION_PATH = "https://raw.githubusercontent.com/isaacebi/Hansard-Malaysia/main/data/session.csv"
PDF_PATH = os.path.join(PARENT_PATH, 'data', 'PDF')
FILE_NAME = os.path.join(PDF_PATH, 'hansard_')
ATTENDENCE = os.path.join(PARENT_PATH, 'data', 'attendance.csv')
ABSENCE = os.path.join(PARENT_PATH, 'data', 'absence.csv')
PENGGAL = os.path.join(PARENT_PATH, 'data', 'penggal.csv')
COMPILE = os.path.join(PARENT_PATH, 'data', 'compile.xlsx')

# %%
df = pd.read_csv(SESSION_PATH, parse_dates=['date'])
df.date = df.date.dt.date
sessions = df.session.tolist()
session_date = dict(zip(df.session,df.date))

# create folder if not exist
isExist = os.path.exists(PDF_PATH)
if not isExist:
    os.makedirs(PDF_PATH)

#%% to download
for recon in range(1, 10):
    try:
        for s in sessions:
            tdate = session_date[s].strftime('%d%m%Y')
            url_hansard = 'https://www.parlimen.gov.my/files/hindex/pdf/DR-' + tdate +  '.pdf'

            isExist = os.path.exists(FILE_NAME + s + '.pdf')
            if not isExist:
                urllib.request.urlretrieve(url_hansard, FILE_NAME + s + '.pdf')
                time.sleep(10) # estimated run 85 * 10 = 850 seconds -> more than 15 minutes

    except URLError:
        time.sleep(120) # sleep 2 minutes

# %% create attendence file
attendance_start = date(2021,7,26)

ss = pd.read_csv(SESSION_PATH, dtype=str)
ss.date = pd.to_datetime(ss.date).dt.date
ss = ss[ss.date >= attendance_start]
sessions = ss.session.tolist()
session_date = dict(zip(ss.session,ss.date))

# mp = pd.read_csv(MP_PATH, usecols=['seat_code','seat','mp'])
mp = pd.read_csv(MP_PATH)
mp['seat_search'] = ['(' + ''.join(x.split()).lower() + ')' for x in mp.seat.tolist()]

df = pd.DataFrame(columns=['date'] + mp.seat_code.tolist())

# Strategy
# Step 1: Use the phrase "Senarai Kehadiran" to find the page where the present list starts
# Step 2: Use the phrase "Tidak Hadir" to find the page where the absent list starts
# Step 3: Extract text from these pages, join, and remove anything after the "tidak hadir" phrase
# Step 4: Encode everyone as absent; encode as present if in string from Step 3

def attendedSession(seat,string): return 1 if seat in string else 0

notPDF = []
for s in sessions:
    try:
        pdf_active = PyPDF2.PdfFileReader(open(FILE_NAME + s + '.pdf', 'rb', ),strict=False)

    except:
        tdate = session_date[s].strftime('%d%m%Y')
        notPDF.append(tdate)
        continue

    n_pages = pdf_active.numPages
    extract_start = 0
    start_set = 0
    extract_end = 0
    for i in range(n_pages):
        page_active = ''.join(pdf_active.getPage(i).extractText().split()).lower()
        if start_set == 0 and ('senaraikehadiran' in page_active or 'ahliyanghadir' in page_active):
            extract_start = i
            start_set = 1 # ensure first instance is taken and frozen
        if 'yangtidakhadir' in page_active: extract_end = i
        if extract_start > 0 and extract_end > 0: break # break the moment we find the end of the section

    res = extract_text(FILE_NAME + s + '.pdf',page_numbers=[x for x in range(extract_start,extract_end+1)])
    res = ''.join(res.split()).lower()
    res = res.split('yangtidakhadir')[0]
    res = res.replace('(johorbaru)','(johorbahru)')

    attendance = [attendedSession(x,res) for x in mp.seat_search.tolist()]
    df.loc[len(df)] = [session_date[s]] + attendance

df = df.set_index('date').transpose()
df['total'] = df.sum(axis=1)
session_dates = list(df.columns)
df = df.reset_index().rename(columns={'index':'seat_code'})
df = pd.merge(df,mp,on=['seat_code'],how='left')
df = df[['seat_code','seat','personal_name', 'current_party'] + session_dates]
df.to_csv(ATTENDENCE,index=False)

# %% create absence file
attendance_start = date(2021,7,26)

ss = pd.read_csv(SESSION_PATH, dtype=str)
ss.date = pd.to_datetime(ss.date).dt.date
ss = ss[ss.date >= attendance_start]
sessions = ss.session.tolist()
session_date = dict(zip(ss.session,ss.date))

# mp = pd.read_csv(MP_PATH, usecols=['seat_code','seat','mp'])
mp['seat_search'] = ['(' + ''.join(x.split()).lower() + ')' for x in mp.seat.tolist()]

df = pd.DataFrame(columns=['date'] + mp.seat_code.tolist())

# Strategy
# Step 1: Use the phrase "Senarai Kehadiran" to find the page where the present list starts
# Step 2: Use the phrase "Tidak Hadir" to find the page where the absent list starts
# Step 3: Extract text from these pages, join, and remove anything after the "tidak hadir" phrase
# Step 4: Encode everyone as absent; encode as present if in string from Step 3

def attendedSession(seat,string): return 1 if seat in string else 0

# for s in sessions:
for s in sessions:
    pdf_active = PyPDF2.PdfFileReader(open(FILE_NAME + s + '.pdf', 'rb', ),strict=False)
    n_pages = pdf_active.numPages
    extract_start = 0
    start_set = 0
    extract_end = 0
    end_hook = ''
    for i in range(n_pages):
        page_active = ''.join(pdf_active.getPage(i).extractText().split()).lower()
        if start_set == 0 and 'ahliyangtidakhadir' in page_active:
            extract_start = i
            start_set = 1 # ensure first instance is taken and frozen
        if 'senatoryangtidakhadir' in page_active or 'dewanrakyat' in page_active:
            extract_end = i
            end_hook = 'senatoryangtidakhadir' if 'senatoryangtidakhadir' in page_active else 'dewanrakyat'
        if extract_start > 0 and extract_end > 0: break # break the moment we find the end of the section

    res = extract_text(FILE_NAME + s + '.pdf',page_numbers=[x for x in range(extract_start,extract_end+1)])
    res = ''.join(res.split()).lower()
    res = res.split('ahliyangtidakhadir',1)[1]
    res = res.split(end_hook,1)[0]
    res = res.replace('(johorbaru)','(johorbahru)')

    attendance = [attendedSession(x,res) for x in mp.seat_search.tolist()]
    df.loc[len(df)] = [session_date[s]] + attendance

df = df.set_index('date').transpose()
df['total'] = df.sum(axis=1)
session_dates = list(df.columns)
df = df.reset_index().rename(columns={'index':'seat_code'})
df = pd.merge(df,mp,on=['seat_code'],how='left')
#df = df[['seat_code','seat','mp'] + session_dates]
df = df[['seat_code','seat','personal_name', 'current_party'] + session_dates]
df.to_csv(ABSENCE, index=False)

# %% 
attendance = pd.read_csv(ATTENDENCE)
df_attend = attendance.copy()
df_attend['percentage'] = df_attend.total/len(ss) * 100

color_df = df_attend.style.apply(below_avg, axis=1)

df_byParty = df_attend.groupby('current_party').agg({
    'total': 'sum',
    'seat_code': 'count'
}).reset_index()

df_byParty.columns = ['Party', 'total_attend', 'number_people']
df_byParty['percentage'] = df_byParty['total_attend']*100 / (df_byParty['number_people']*len(ss))
freeze_col = ['seat_code', 'seat', 'personal_name', 'current_party']

penggal_col = pd.read_csv(PENGGAL)

with pd.ExcelWriter(COMPILE) as writer:
    color_df.to_excel(writer,
                        index=False,
                        sheet_name='All')
    
    df_byParty.to_excel(writer,
                        index=False,
                        sheet_name='ByParty')

    for i in penggal_col.T:
        cleanList = [x for x in penggal_col.T[i].tolist() if str(x) != 'nan']
        dft_ = df_attend[freeze_col+cleanList]
        dft_['total'] = dft_.iloc[:, 4:].sum(axis=1)

        dft_.to_excel(writer,
                    index=False,
                    sheet_name=f'split_{i+1}')

# %%
