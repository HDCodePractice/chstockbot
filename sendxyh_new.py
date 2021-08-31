import getopt,sys,config,os
import datetime
from telegram import Bot
from stockutil import stooq, wikipedia
from stockutil.ticker import Ticker, TickerError
from util.utils import sendmsg
from stockutil.index import Index, IndexError
target_date = datetime.date.today()

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

    ENV = config.ENV

    bot = Bot(token = ENV.BOT_TOKEN)
    symbols = ENV.XYHTICKER
    notifychat = ENV.XYHCHAT
    adminchat = ENV.XYHLOG
    debug = ENV.DEBUG
    ds = ENV.XYHSOURCE
    xyhindexindex = ENV.XYHINDEX
    notify_message = ""
    admin_message = ""
    xyh_msg = ""
    msg  = ""
    try: #ndx 和spx成分股的计算
        for source,value in Index.sources.items(): #计算指数的内容
            index = Index(source, "sources",local_store=config.config_path)
            index.get_tickers_list()
            try:
                index.compare_avg_ma(ma=50,end_date=target_date)
            except IndexError as e:
                continue
            try:
                msg += index.gen_index_msg(target_date)
            except IndexError as e:
                admin_message += f"{e}"
                continue
    except Exception as err:
        admin_message += f"{type(err)}:\n{err}"
    
    try: #市场成分股的计算
        for market in Index.markets: #
            index = Index(market,"markets",local_store=config.config_path)
            index.get_tickers_list()
            try:
                index.compare_avg_ma(ma=50,end_date=target_date)
            except IndexError as e:
                continue
            try:
                msg += index.gen_index_msg(target_date)
            except IndexError as e:
                admin_message += f"{e}"
                continue
    except Exception as err:
        admin_message += f"{type(err)}:\n{err}"

    try:    
        for datasource in ds:
            for symbol in symbols:
                ticker = Ticker(symbol[0],"web",datasource,endtime=target_date)
                try:
                    ticker.load_data()
                    xyh_msg += ticker.get_today_price_msg()
                    for ma in symbol[1:]:
                        ticker.cal_symbols_avg(ma)
                        ticker.cal_sams_change_rate()
                except TickerError as e:
                    admin_message += f"{e}\n"
                    continue
                xyh_msg += f"{ticker.gen_xyh_msg()}\n"
            break
    except Exception as err:
        admin_message += f"{type(err)}:\n{err}\n"
    
    if xyh_msg:
        notify_message += f"🌈🌈🌈{target_date}天相🌈🌈🌈: \n\n{xyh_msg}\n{msg}\n贡献者:毛票教的大朋友们\n"
        sendmsg(bot,notifychat,notify_message,debug=debug)
    if admin_message:
        admin_message = f"今天完蛋了，什么都不知道，快去通知管理员，bot已经废物了，出的问题是:\n{admin_message}"
        sendmsg(bot,adminchat,admin_message,debug=debug)
    

    