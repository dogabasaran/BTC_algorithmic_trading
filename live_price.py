import requests
from bs4 import BeautifulSoup
import time
import os
import numpy as np
from tqdm import tqdm
import datetime
import csv
'''
TODO:
Change sma code, dont calculate and display until full range is captured. (at the start)
log trades onto xl file
introduce commission into trades
epsilon: large enough difference for trades
calculate moving average gradients
'''
startTime = datetime.datetime.now()
cap = 1000

wma = []

# Countdown clock
def countdown(t):
    while t:
        mins, secs = divmod(t,60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        print(timeformat, end='\r')
        time.sleep(1)
        t -= 1
    print("New data entry")

# Function to scrape price from website
def get_price():
    url = 'https://coinmarketcap.com/currencies/bitcoin/'
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    value = soup.find('span', {'class': "cmc-details-panel-price__price"})
    btc_price = format_price(value.text)
    return btc_price

# Formats scraped price data into float
def format_price(price):
    price = str(price)
    formatted_price = price.replace('$','').replace(',','')
    formatted_price = float(formatted_price)
    return formatted_price

# Adds price to a list, removes oldest price according to give max range
def get_sma(sma, price, movingrange):
    sma.append(price)
    if len(sma)>movingrange:
        sma.pop(0)
    return sma

# Calculates weighted moving average of 10 last prices
def get_wma10(sma):
    if len(sma)==10:
        w = np.linspace(1,10,10)
        wma_price = np.round(np.dot(w,sma)/w.sum(),2)
    else:
        wma_price = 'NULL'

    return wma_price


# Function to decide on long/short position.
def decide_position(shorter_ma,longer_ma, prev_position=2):
    if shorter_ma > longer_ma:
        position = 1
        pos = 'long (hold btc)'
    elif shorter_ma < longer_ma:
        position = 2
        pos = 'short (hold cash)'
    else:
        pos = 'not defined (ma\'s equal)'
        position = prev_position
    print('Recommended position: ' + pos)
    return position


def trade_long(cash, price):
    btc = cash/price
    print("Bought BTC")
    return btc

def trade_short(btc, price):
    cash = btc * price
    print("Sold BTC")
    return cash

def make_trade(position_history, cap, price):

    if position_history[0] != position_history[1]:

        if (position_history[0] == 1) and (position_history[1] == 2): # it goes 1 --> 2
            cap = trade_short(cap,price)
            return cap

        elif (position_history[0] == 2) and (position_history[1] == 1): # it goes 2 --> 1
            cap = trade_long(cap,price)
            return cap

    elif position_history[0] == position_history[1]:
        # No trade
        return cap

def display_assets(position, cap, price):
    if position == 1: # holding btc
        print("Total capital: {} BTC, equivalent to {} USD".format(np.round(cap,7), np.round(cap*price,2)))
    if position == 2: # holding cash
        print("Total capital: {} USD, equivalent to {} BTC".format(np.round(cap,2), np.round(cap/price,7)))


def write_to_excel():
    data_to_write = [str(datetime.datetime.now()),"buy/sell action",'USD equ..']
    with open('tradebook.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data_to_write)

sma = []
sma2 = []
position_history = [2]

while True:
    os.system('cls')
    currentTime = datetime.datetime.now()
    print('Started program at: {}, current time: {}'.format(startTime.strftime("%Y-%m-%d %H:%M:%S"), currentTime.strftime("%Y-%m-%d %H:%M:%S")))
  
    price = get_price()
    print('Current Price: ${}'.format(price))

    
    #write_to_excel()

    SHORT_SMA_RANGE = 10
    LONG_SMA_RANGE = 30
    
    sma = get_sma(sma, price, SHORT_SMA_RANGE)
    if len(sma) ==  SHORT_SMA_RANGE:
        sma_price = np.round(np.mean(sma),2)
        wma_price = get_wma10(sma)

        print('sma10: {}'.format(sma_price))
        print('wma10: {}'.format(wma_price))

        
    sma2 = get_sma(sma2, price, LONG_SMA_RANGE)
    if len(sma2) == LONG_SMA_RANGE:
        sma2_price = np.round(np.mean(sma2),2)
        print('sma30: {}'.format(sma2_price))
        
    if len(sma2) == LONG_SMA_RANGE:
        position = decide_position(wma_price, sma2_price, position_history[-1])

        position_history.append(position)
        if len(position_history)>2:
            position_history.pop(0)
        
        cap = make_trade(position_history, cap, price)
        display_assets(position, cap, price)
    else:
        print("Not enough data to make decision and trades. Gathering data.")

    # Refresh every
    countdown(60)

