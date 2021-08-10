import getopt,sys,config,os
from stockutil.ticker import Ticker, TickerError, get_week_num
from bot import sendmsg
import datetime
from telegram import Bot

start_date = datetime.date(2021,1,1)
end_date = datetime.date.today()

def help():
    return "'sendxyh.py -c configpath -s yyyymmdd -e yyyymmdd'"


def ge_mmt_msg(symbol, start, end, freq='W-WED', week_num =2):
    s = Ticker(symbol, end)
    error_msg = ""
    try:
        s.load_data(source = "stooq")
        s.get_date_list(start=start, end=end, freq='W-WED')
        s.get_price_lists(week_num =2)
        price_list = s.get_price_lists()
        #print (price_list)
        weekly_profit_info = s.cal_profit('weekly')
        monthly_profit_info = s.cal_profit('montly')

        weekly_msg = f"如果从{start}开始，每周三定投{symbol.upper()} 100元，截止到{end}，累计投入{weekly_profit_info['cost']}，市值为{weekly_profit_info['value']}，利润率为 {weekly_profit_info['rate']}"

        monthly_msg = f"如果从{start}开始，每月第二周的周三定投{symbol.upper()} 100元，截止到{end}，累计投入{monthly_profit_info['cost']}，市值为{monthly_profit_info['value']}，利润率为 {monthly_profit_info['rate']}"
    except TickerError as e:
        error_msg += str(e) 

    return {'weekly':weekly_msg, 'monthly':monthly_msg, 'admin':error_msg}



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
            msg = ge_mmt_msg(symbol, start_date, end_date, freq='W-WED', week_num =2)
            weekly_msg += f"{msg['weekly']}\n"
            monthly_msg += f"{msg['monthly']}\n"
            notify_msg = f"{weekly_msg}\n{monthly_msg}"
            admin_msg += msg['admin']

        if get_week_num(end_date.year,end_date.month,end_date.day) == 2:
            sendmsg(bot,mmtchat,f"{mmt_month}\n{notify_msg}",debug)
        else:
            sendmsg(bot,mmtchat,f"{mmt_week}\n{notify_msg}",debug)
        if admin_msg:
            sendmsg(bot, adminchat,admin_msg, debug)
    except Exception as err:
       sendmsg(bot,adminchat,f"今天完蛋了，什么都不知道，快去通知管理员，bot已经废物了，出的问题是:\n{type(err)}:\n{err}",debug)
