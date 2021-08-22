import getopt,sys,config,os
from stockutil.ticker import Ticker, TickerError
from util.utils import get_dmm_maxtry,get_xmm_maxtry, get_week_num, sendmsg
import datetime
from telegram import Bot

start_date = datetime.date(2021,1,1)
end_date = datetime.date.today()

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
                start_date = datetime.datetime.strptime(arg,"%Y%m%d").date()
            except:
                print(f"无法读取日期：\n{help()}")
                sys.exit(2)
        elif opt in ("-e", "--endtime"):
            try: #尝试对从参数中读取的日期进行日期格式转换，如果没有参数，则使用1/26/2021
                end_date = datetime.datetime.strptime(arg,"%Y%m%d").date()
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
    admin_msg = ""
    notify_msg = ""
    
    
    mmt_week = "如果你每周定投，那么今天是投 #小毛毛 的日子啦，今天是周三 请向小🐷🐷中塞入你虔诚的🪙吧～"
    mmt_month = f"如果你每月定投，那么今天是投 #大毛毛 的日子啦，今天是本月第二周的周三 请向小🐷🐷中塞入你虔诚的💰吧～\n{mmt_week}"

    weekly_msg = ""
    monthly_msg = ""

    try:
        for symbol in symbols:
            try:
                ticker = Ticker(symbol, start_date = start_date, end_date=end_date)
                ticker.load_data('stooq')
                ticker.get_price_list('xmm',get_xmm_maxtry)
                ticker.get_price_list('dmm',get_dmm_maxtry)
                ticker.ge_profit_msg()
                weekly_msg += f"{ticker.profit_msg['weekly']}\n"
                monthly_msg += f"{ticker.profit_msg['montly']}\n"
                notify_msg = f"{weekly_msg}\n{monthly_msg}"
            except TickerError as e:
                admin_msg += str(e)

        if get_week_num(end_date.year,end_date.month,end_date.day) == 2:
            sendmsg(bot,mmtchat,f"{mmt_month}\n\n{notify_msg}",debug)
        else:
            sendmsg(bot,mmtchat,f"{mmt_week}\n\n{notify_msg}",debug)
        if admin_msg:
            sendmsg(bot, adminchat,admin_msg, debug)
    except Exception as err:
       sendmsg(bot,adminchat,f"今天完蛋了，什么都不知道，快去通知管理员，bot已经废物了，出的问题是:\n{type(err)}:\n{err}",debug)
