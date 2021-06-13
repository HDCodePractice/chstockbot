import pandas as pd
import pandas_datareader as pdr
import datetime
from telegram import Update, ForceReply, Bot, botcommand
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import numpy as ny
import pandas_datareader.data as web
from pandas import DataFrame
import mysystemd
import os
import getopt
import sys
import config


def help():
    return "'sendxyh.py -c <configpath>'"


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:", ["config="])
    except getopt.GetoptError:
        print(help())
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(help())
            sys.exit()
        elif opt in ("-c", "--config"):
            config.config_path = arg          

    config.config_file = os.path.join(config.config_path, "config.json")
    try:
        CONFIG = config.load_config()
    except FileNotFoundError:
        print(f"config.json not found.Generate a new configuration file in {config.config_file}")
        config.set_default()
        sys.exit(2)

end = datetime.date.today()
start = end - datetime.timedelta(days=365)



a = ["TCTZF","600019.SS","MZDAY"]
b = [13,50,200]

mesg = ""
xyh_id = 841121769

for j in a :
    df = web.DataReader(j,"yahoo",start=start,end=end )
    close = df.tail(1).iat[0,3]
    low = df.tail(1).iat[0,1]
    high = df.tail(1).iat[0,0]
    print( f"""{j}价格: 收盘{close} (最低{low}-最高{high})""")# for test
    mesg += f"""{j}价格: 收盘{close} (最低{low}-最高{high})"""

    for i in b :
    
        print(f"{i} 周期均价：{df.tail(i)['Adj Close'].mean()}") # for test
        mesg += f"{i} 周期均价：{df.tail(i)['Adj Close'].mean()}"
"""
def thin(a):        
    return f"{a}"
for i in a :
    mesg += thin(a)
    print(f"这是一次的结果{thin(i)}")
"""
print(f"所有的结果{mesg}")# for test


bot = Bot(token=CONFIG["Token"])
bot.send_message(chat_id=xyh_id,text=mesg)