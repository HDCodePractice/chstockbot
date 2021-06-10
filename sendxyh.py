import telegram
from telegram import Update, Bot   
from telegram.ext import CommandHandler,  CallbackContext
from numpy import append
import config
import os
import getopt
import sys
import pandas as pd
import pandas_datareader as pdr
import datetime


groups =[-1001409640737,-1001250988031,-1001478922081,-1001405840327]

start = datetime.date.today() - datetime.timedelta(days=365) 
end = datetime.date.today()

tickers = ['qqq','spy','nio','aapl','msft']

market_brief = ""

def brief(ticker, term1, term2, term3):
    df_ticker = pdr.get_data_yahoo(ticker.upper(),start=start,end=end)
    ticker_today = df_ticker.iat[-1,3]
    ticker_today_low = df_ticker.iat[-1,1]
    ticker_today_high = df_ticker.iat[-1,0]
    ticker_term1 = df_ticker.tail(term1)["Adj Close"].mean()
    ticker_term2 = df_ticker.tail(term2)["Adj Close"].mean()
    ticker_term3 = df_ticker.tail(term3)["Adj Close"].mean()
    
    ticker_brief = f"""{ticker} 今日：{format(ticker_today,'.2f')}({format(ticker_today_low,'.2f')}-{format(ticker_today_high,'.2f')}) {term1} 周期均价：{format(ticker_term1,'.2f')} {term2} 周期均价：{format(ticker_term2,'.2f')} {term3} 周期均价：{format(ticker_term3,'.2f')}"""
    return[ticker_brief]

for t in tickers:
    market_brief += f"{brief(t, 13, 50, 200)}\n"
    #print(f"{brief(t, 13, 50, 200)}")
#print(f"今日天相\n{market_brief}")



config.config_file = os.path.join(config.config_path, "config.json")
try:
        CONFIG = config.load_config()
except FileNotFoundError:
        print(f"config.json not found.Generate a new configuration file in {config.config_file}")
        config.set_default()
        sys.exit(2)

bot = Bot(CONFIG["Token"])
for g in groups:    
    bot.send_message(chat_id = g, text = f"今日天相\n{market_brief}")