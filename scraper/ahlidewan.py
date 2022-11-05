# %%
from urllib.error import URLError
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os
import time
import re

# %%
PARENT_PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
DATA_PATH = os.path.join(PARENT_PATH, 'data')
AHLI_DEWAN = os.path.join(DATA_PATH, 'ahliDewan.csv')
AHLI_DEWAN2 = os.path.join(DATA_PATH, 'ahliDewan2.csv')

# %%
BASE_URL = 'https://www.parlimen.gov.my/'
AHLI_DEWAN_URL = 'https://www.parlimen.gov.my/ahli-dewan.html?uweb=dr&'

# %%
res = requests.get(AHLI_DEWAN_URL)
soup = BeautifulSoup(res.text, 'html.parser')

url_ahli_dewan = []
url_img = []

for table in soup.find_all('ul', {'class': 'list tiles member-of-parliament'}):

    for link in table.find_all('a', href=True):
        url_ahli_dewan.append(link['href'])

    for image in table.find_all('img'):
        url_img.append(image['src'])

# %%
lis_ahli_dewan = []

for i, url in enumerate(url_ahli_dewan):
    is_url = BASE_URL + '/' + url # each parlimen URL
    print(is_url)

    for recon in range(20):
        try:
            table = pd.read_html(is_url)
            time.sleep(10)
            image_url = BASE_URL + url_img[i]
            ahli_ = {
                'Nama': np.nan,
                'Parti': np.nan,
                'Jawatan dalam Parlimen': np.nan,
                'Jawatan dalam Kabinet': np.nan,
                'Tempat Duduk': np.nan,
                'Parlimen': np.nan,
                'Kawasan': np.nan,
                'Negeri': np.nan,
                'No. Telefon': np.nan,
                'No. Faks': np.nan,
                'Email': np.nan,
                'Alamat Surat-menyurat': np.nan,
                'image_URL': image_url
            }

            for index, row in table[1].iterrows():
                ahli_[row[0]] = row[1]

            lis_ahli_dewan.append(ahli_)
            break

        except URLError:
            print('break')
            time.sleep(120) # sleep 2 minutes


df = pd.DataFrame(lis_ahli_dewan)
df.to_csv(AHLI_DEWAN) # original

# %%
df2 = df.copy()
df2['Nama'] = df2['Nama'].str.replace('YB', '')
df2['Nama'] = df2['Nama'].str.replace('YAB', '')

df2['Nama'] = df2['Nama'].str.lower()
df2['Nama'] = df2['Nama'].str.title()

df2['Nama'] = df2['Nama'].str.replace('A/L', 'a/l')
df2['Nama'] = df2['Nama'].str.replace('A/P', 'a/p')  
df2['Nama'] = df2['Nama'].str.replace('Bin', 'bin')

df2['Nama'] = df2['Nama'].str.replace('Datuk Ignatius Dorell Leiking', 'Datuk Ignatius Darell Leiking')
df2['Nama'] = df2['Nama'].str.replace('Datuk Seri Panglima Hajah Azizah binti Datuk Seri Panglima Haji Mohd Dun', 'Dato Hajah Azizah binti Mohd Dun')
df2['Nama'] = df2['Nama'].str.replace('Tuan M. Kulasegaran a/l V. Murugeson', 'Tuan M. Kulasegaran')  
df2['Nama'] = df2['Nama'].str.replace('Puan Isnaraissah Munirah Bt Majilis @ Fakharudy', 'Puan Isnaraissah Munirah binti Majilis @ Fakharudy')
df2['Nama'] = df2['Nama'].str.replace('Datuk Seri Haji Mohd Salim Sharif', 'Dato Haji Salim Shariff')
df2['Nama'] = df2['Nama'].str.replace('Tuan MaMun bin Sulaiman', 'Tuan Mamun bin Sulaiman')
df2['Nama'] = df2['Nama'].str.replace('Datuk Seri Panglima Madius bin Tangau', 'Datuk Seri Panglima Wilfred Madius Tangau')


df2['Nama'] = df2['Nama'].str.replace("'", "")
df2['Nama'] = df2['Nama'].str.replace("(", "")
df2['Nama'] = df2['Nama'].str.replace(")", "")
df2['Nama'] = df2['Nama'].apply(lambda x: ' '.join(x.split()))
df2['Nama'] = df2['Nama'].apply(lambda x: ' @ '.join(x.split('@')))
df2['Nama'] = df2['Nama'].apply(lambda x: re.sub(' +', ' ', x))

df2['Kawasan'] = df2.Kawasan.str.lower()
df2['Kawasan'] = df2.Kawasan.str.title()
df2['Kawasan'] = df2.Kawasan.str.replace('Di-', 'di-')

df2.to_csv(AHLI_DEWAN2) # version 2 - for diaolog extraction

# %%
