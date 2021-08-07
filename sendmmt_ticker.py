import getopt,sys,config,os
import pandas_datareader.data as web
import datetime 
#from datetime import date
import pandas as pd
from telegram import Bot
from stockutil import ticker, stooq
from bot import sendmsg

start = datetime.date(2021,7,1)
end = datetime.date.today()

def help():
    return "sendxyh.py -c configpath -s yyyymmdd -e yyyymmdd"

def get_week_num(year, month, day):
    """
    获取当前日期是本月的第几周
    """
    start = int(datetime.date(year, month, 1).strftime("%W"))
    end = int(datetime.date(year, month,day).strftime("%W"))
    week_num = end - start + 1
    return week_num

def ge_mmt_msg(symbol, start, end, freq='W-WED', week_num =2):
    s = ticker.Ticker(symbol, end)
    error_msg = ""
    try:
        s.load_data(source = "stooq")
        price_list = s.get_price_lists(start=start, end=end, freq='W-WED', week_num =2)
        #print (price_list)
        weekly_profit_info = s.cal_profit(price_list['weekly'])
        monthly_profit_info = s.cal_profit(price_list['montly'])
        weekly_msg = f"如果从{start}开始，每周三定投{symbol.upper()} 100元，截止到{end}，累计投入{weekly_profit_info['cost']}，市值为{weekly_profit_info['value']}，利润率为 {weekly_profit_info['rate']}"
        monthly_msg = f"如果从{start}开始，每月第二周的周三定投{symbol.upper()} 100元，截止到{end}，累计投入{monthly_profit_info['cost']}，市值为{monthly_profit_info['value']}，利润率为 {monthly_profit_info['rate']}"
    except ticker.TickerError as e:
        error_msg += str(e) 

    return {'weekly':weekly_msg, 'monthly':monthly_msg, 'error':error_msg}

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
        elif opt in ("-s", "--starttime"): 
            try:
                y,m,d = arg[:4],arg[-4:-2],arg[-2:]
                start = datetime.date(int(y),int(m),int(d)) 
            except:
                print(f"无法读取日期：\n{help()}")
                sys.exit(2)
        elif opt in ("-e", "--endtime"):
            try: 
                y,m,d = arg[:4],arg[-4:-2],arg[-2:]
                end = datetime.date(int(y),int(m),int(d))
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


    mmt_week = "如果你每周定投，那么今天是投 #小毛毛 的日子啦，今天是周三 请向小🐷🐷中塞入你虔诚的🪙吧～"
    mmt_month = f"如果你每月定投，那么今天是投 #大毛毛 的日子啦，今天是本月第二周的周三 请向小🐷🐷中塞入你虔诚的💰吧～\n{mmt_week}"

    weekly_profit_msg = ""
    monthly_profit_msg = ""
    err_msg = ""

    for symbol in symbols:
        msg = ge_mmt_msg(symbol, start, end, freq='W-WED', week_num =2)
        weekly_profit_msg += f"{msg['weekly']}\n"
        monthly_profit_msg += f"{msg['monthly']}\n"
        err_msg += msg['error']

    if get_week_num(end.year,end.month,end.day) == 2:
        sendmsg(bot,mmtchat,f"{mmt_month}\n{monthly_profit_msg}",debug)
    else:
        sendmsg(bot,mmtchat,f"{mmt_week}\n{weekly_profit_msg}",debug)