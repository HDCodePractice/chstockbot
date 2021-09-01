import getopt,sys,config,os
import datetime
from telegram import Bot
from stockutil.ticker import Ticker
from util.utils import is_second_wednesday,sendmsg

target_end_time = datetime.date.today()
target_start_time = datetime.date(2021,1,1)

def help():
    return "sendmmt.py -c configpath -s yyyymmdd -e yyyymmdd"

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
            try: #尝试对从参数中读取的日期进行日期格式转换，如果没有参数，则使用20210126
                target_start_time = datetime.datetime.strptime(arg,"%Y%m%d").date()
            except:
                print(f"无法读取起始日期：{arg}\n{help()}")
                sys.exit(2)
        elif opt in ("-e", "--endtime"):
            try: #尝试对从参数中读取的日期进行日期格式转换，如果没有参数，则使用1/26/2021
                target_end_time = datetime.datetime.strptime(arg,"%Y%m%d").date()
            except:
                print(f"无法读取结束日期：{arg}\n{help()}")
                sys.exit(2) 

    config.config_file = os.path.join(config.config_path, "config.json")
    try:
        CONFIG = config.load_config()
    except FileNotFoundError:
        print(f"config.json not found.Generate a new configuration file in {config.config_file}")
        config.set_default()

    ENV = config.ENV
    print(f"sendmmt {target_end_time} ....")

    if ENV.BOT_TOKEN == "":
        sys.exit()

    bot = Bot(token = ENV.BOT_TOKEN)
    symbols = ENV.MMTTICKER
    mmtchat = ENV.MMTCHAT
    adminchat = ENV.XYHLOG
    debug = ENV.DEBUG
    ds = ENV.XYHSOURCE
    
    admin_message = ""
    notify_message = ""

    try:
        for symbol in symbols:
            ticker = Ticker(symbol,"web","stooq",target_start_time,target_end_time)
            ticker.load_data()
            ticker.cal_profit()
            mmt_msg = ticker.gen_mmt_msg()
            notify_message += f"{mmt_msg}\n"
        if ticker.xmm_profit:
            notify_message = f"今天是周三，到了投 #小毛毛 的日子啦，请向小🐷🐷中塞入你虔诚的🪙吧～\n\n{notify_message}\n{ENV.CONTRIBUTORS}"
        if is_second_wednesday(d=target_end_time):
            notify_message = f"今天是本月第二周的周三，到了投 #大毛毛 的日子啦， 请向小🐷🐷中塞入你虔诚的💰吧～\n\n{notify_message}\n"
        if notify_message:
            sendmsg(bot,mmtchat,notify_message,debug=debug)
    except Exception as err:
        sendmsg(bot,adminchat,f"今天完蛋了，什么都不知道，快去通知管理员，bot已经废物了，出的问题是:\n{type(err)}:\n{err}",debug)
        raise err