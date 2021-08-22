import getopt,sys,config,os
from pandas.core.indexing import IndexSlice
import datetime
from telegram import Bot
from stockutil.ticker import Ticker, TickerError
from stockutil.index import Index, IndexError
from util.utils import sendmsg

target_date = datetime.date.today()
start_date = datetime.date(2021,1,1)

def help():
    return "sendxyh.py -c configpath -d yyyymmdd"

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:d:", ["config, datetime="])
    except getopt.GetoptError:
        print(help())
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(help())
            sys.exit()
        elif opt in ("-c", "--config"):
            config.config_path = arg          
        elif opt in ("-d", "--datetime"): 
            try:
                y,m,d = arg[:4],arg[-4:-2],arg[-2:]
                target_date = datetime.date(int(y),int(m),int(d))
            except Exception:
                print("日期无法解读")
                print(help())
                sys.exit(2)

    config.config_file = os.path.join(config.config_path, "config.json")
    try:
        CONFIG = config.load_config()
    except FileNotFoundError:
        print(f"config.json not found.Generate a new configuration file in {config.config_file}")
        config.set_default()
        sys.exit(2)

    bot = Bot(token = CONFIG['Token'])
    symbols = CONFIG['xyhticker']
    indexs = CONFIG['xyhindex']
    notifychat = CONFIG['xyhchat']
    adminchat = CONFIG['xyhlog']
    debug = CONFIG['DEBUG']

    notify_message = ""
    admin_message = ""
    index_message = ""

    for index in indexs:
        try:
            s = Index(index)
            s.get_index_tickers_list()              
            s.compare_avg(ma = 50,source = "~/Downloads/data", start_date = start_date, end_date=target_date)
            s.ge_index_compare_msg(index, end_date=datetime.date(2021,7,21))            
            index_message += f"{s.index_msg}\n"
            admin_message += f"{s.compare_msg['err']}"
        except IndexError as e:
            admin_message += str(e)

    for symbol in symbols:
        try:               
            ticker = Ticker(symbol[0], start_date = start_date, end_date=target_date)
            ticker.load_data('stooq')
            ticker.ge_xyh_msg(symbol[1:])
            notify_message += f"{ticker.xyh_msg}"
        except TickerError as e:
            admin_message += str(e)
    try:
        if admin_message:
            sendmsg(bot,adminchat,admin_message,debug=debug)
        if notify_message:
            notify_message = f"🌈🌈🌈{target_date}天相🌈🌈🌈: \n\n{notify_message}\n{index_message}\n贡献者:毛票教的大朋友们"
            sendmsg(bot,notifychat,notify_message,debug=debug)
    except Exception as err:
        sendmsg(bot,adminchat,f"今天完蛋了，什么都不知道，快去通知管理员，bot已经废物了，出的问题是:\n{type(err)}:\n{err}",debug)
