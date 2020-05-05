import requests
from bs4 import BeautifulSoup
import time
import os
import numpy as np
from tqdm import tqdm
'''
TODO: 
add comments
add runtime displayer
give it $1000
make triggers for when position changes
calculate moving average gradients
'''
wma = []

def get_price():
    url = 'https://coinmarketcap.com/currencies/bitcoin/'
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    value = soup.find('span', {'class': "cmc-details-panel-price__price"})
    btc_price = format_price(value.text)
    return btc_price

def format_price(price):
    price = str(price)
    formatted_price = price.replace('$','').replace(',','')
    formatted_price = float(formatted_price)
    return formatted_price

def get_sma(sma, price, movingrange):
    sma.append(price)
    if len(sma)>movingrange:
        sma.pop(0)
    return sma

def get_wma10(sma):
    if len(sma)==10:
        w = np.linspace(1,10,10)
        wma_price = np.round(np.dot(w,sma)/w.sum(),2)
    else:
        wma_price = 'NULL'

    return wma_price

def position(shorter_ma,longer_ma):
    if shorter_ma > longer_ma:
        position = 'long (hold btc)'
    elif shorter_ma < longer_ma:
        position = 'short (hold cash)'
    else:
        position = 'not defined (ma\'s equal)'

    print('Recommended position: ' + position)


sma = []
sma2 = []

while True:
    os.system('cls')
    price = get_price()

    sma = get_sma(sma, price,5)
    sma_price = np.round(np.mean(sma),2)
    sma2 = get_sma(sma2, price,10)
    sma2_price = np.round(np.mean(sma2),2)
    wma_price = get_wma10(sma2)

    print('Current Price: ${}'.format(price))
    print('sma5: {}'.format(sma_price))
    print('sma10: {}'.format(sma2_price))
    print('wma10: {}'.format(wma_price))
    position(sma_price, sma2_price)

    for i in tqdm(range(60)):
        time.sleep(1)

