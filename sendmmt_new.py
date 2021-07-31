import getopt,sys,config,os
from stockutil.ticker import Ticker,sendmsg
from numpy import e
import pandas_datareader.data as web
import datetime
import pandas as pd
from telegram import Bot
from sendxyh import sendmsg

target_end_time = datetime.date.today()
target_start_time = datetime.date(2021,1,1)

def help():
    return "'sendxyh.py -c configpath -s yyyymmdd -e yyyymmdd'"

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:s:e:", ["config=","starttime=","endtime="])
    except getopt.GetoptError:
        print(help())
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(help())
            sys.exit()
        elif opt in ("-c", "--config"):
            config.config_path = arg  
        elif opt in ("-s", "--starttime"): #setup datetime format "yyyymmdd"
            try: #尝试对从参数中读取的日期进行日期格式转换，如果没有参数，则使用1/26/2021
                target_start_time = datetime.datetime.strptime(arg,"%Y%m%d").date()
            except:
                print(f"无法读取日期：\n{help()}")
                sys.exit(2)
        elif opt in ("-e", "--endtime"):
            try: #尝试对从参数中读取的日期进行日期格式转换，如果没有参数，则使用1/26/2021
                target_end_time = datetime.datetime.strptime(arg,"%Y%m%d").date()
            except:
                print(f"无法读取日期：\n{help()}")
                sys.exit(2)

        

    config.config_file = os.path.join(config.config_path, "config.json")
    try:
        CONFIG = config.load_config()
    except FileNotFoundError:
        print(f"config.json not found.Generate a new configuration file in {config.config_file}")
        config.set_default()
        sys.exit(2)

    bot = Bot(token = CONFIG['Token'])
    symbols = CONFIG['mmtticker']
    adminchat = CONFIG['xyhlog']
    debug = CONFIG['DEBUG']
    ds = CONFIG['xyhsource']   
    mmtchat = CONFIG['mmtchat'] 
    admin_message = ""
    notify_message = ""
    try:
        for symbol in symbols:
            ticker = Ticker(symbol)
            ticker.load_data(type="internet",source="stooq",start=target_start_time,end=target_end_time)
            ticker.cal_profit()
            ticker.generate_mmt_msg(ticker.profit[0],ticker.profit[1])
            admin_message += ticker.admin_msg
            notify_message += ticker.notify_msg
        if admin_message:
            sendmsg(bot,mmtchat,admin_message,debug=debug)
        if notify_message:
            sendmsg(bot,mmtchat,notify_message,debug=debug)
    except Exception as err:
        sendmsg(bot,adminchat,f"今天完蛋了，什么都不知道，快去通知管理员，bot已经废物了，出的问题是:\n{type(err)}:\n{err}",debug)
    
    