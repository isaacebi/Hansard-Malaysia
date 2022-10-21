# %%
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import os
import re
import time

# %% helper function
# to check "seat" is True
def seatCheck(pattern, text):
    if re.search(pattern+"$", text):
        return 1
    else:
        return 0

# %%
PARENT_PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
DATA_PATH = os.path.join(PARENT_PATH, 'data')
MP_PATH = os.path.join(PARENT_PATH, 'data', 'mp_2022-10-10.csv')
JWTN_PATH = os.path.join(PARENT_PATH, 'data', 'jawatankuasa.csv')

HEADER = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0"}

VIEW_URL = [51, 55, 52, 54]
KHAS_VIEW_URL = [
    2099, 2100, 2102, 2103, 2104, 2105, 2106, 2107, 2108, 2250, 2453
]

# %%
mp = pd.read_csv(MP_PATH)


# %% not Khas
for view in VIEW_URL:
    print(view)
    URL = f"https://www.parlimen.gov.my/jawatankuasa-pilihan-khas.html?view={view}&uweb=dr&"
    res = requests.get(URL, headers=HEADER)
    soup = BeautifulSoup(res.content, 'html.parser')
    df = pd.read_html(URL)

    title = soup.select('h5')[0].text.replace('\n', '')

    # pengerusi
    mp[title] = mp.seat.apply(lambda x: seatCheck(x, df[0][1][0]))

    # ahli
    for i in range(len(df[1][0])):
        mp[title] = mp[title] + mp.seat.apply(lambda x: seatCheck(x, df[1][1][i]))

    time.sleep(10)

# %% khas
for view in KHAS_VIEW_URL:
    print(view)
    URL = f"https://www.parlimen.gov.my/jawatankuasa-dr.html?view={view}&uweb=dr&"
    res = requests.get(URL, headers=HEADER)
    soup = BeautifulSoup(res.content, 'html.parser')
    df = pd.read_html(URL)

    title = soup.select('h5')[0].text.replace('\n', '')

    # pengerusi
    mp[title] = mp.seat.apply(lambda x: seatCheck(x, df[0][0][0]))

    # ahli
    for i in range(len(df[1][0])):
        mp[title] = mp[title] + mp.seat.apply(lambda x: seatCheck(x, df[1][0][i]))

    time.sleep(20)
    
# %%
mp.to_csv(JWTN_PATH, index=False)

# %%
