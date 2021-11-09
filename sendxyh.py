import getopt,sys,config,os
import datetime
from telegram import Bot
from stockutil.ticker import Ticker
from stockutil.index import Index
from util.tgutil import split_msg

target_date = datetime.date.today()

def help():
    return "sendxyh.py -c configpath -d yyyymmdd"

def sendmsg(bot,chatid,msg,debug=True):
    if debug:
        print(f"{chatid}\n{msg}")
    else:
        msgs = split_msg(msg)
        for m in msgs:
            bot.sendMessage(chat_id=chatid, text=m)

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
        # sys.exit(2)

    ENV = config.ENV
    print(f"sendxyh {target_date} ....")

    if ENV.BOT_TOKEN == "":
        sys.exit()

    bot = Bot(token = ENV.BOT_TOKEN)
    symbols = ENV.XYHTICKER
    notifychat = ENV.XYHCHAT
    adminchat = ENV.XYHLOG
    debug = ENV.DEBUG
    ds = ENV.XYHSOURCE
    indexs = ENV.XYHINDEX
   

    notify_message = ""
    admin_message = ""

    try:
        # 计算指定ETF的均线价格与偏离度
        print("计算指定ETF的均线价格与偏离度")
        for symbol in symbols:
            print(f"{symbol}")
            t = Ticker(symbol[0],from_s="web",ds="stooq",endtime=target_date)
            for ma in symbol[1:]:
                t.cal_symbols_avg(int(ma))
            notify_message += f"{t.get_today_price_msg()}{t.gen_xyh_msg()}\n"
        
        # 计算NDX和SPX成分股高于50MA的比例和交易量变化
        print("计算NDX和SPX成分股高于50MA的比例和交易量变化")
        for index in indexs:
            print(f"{index}")
            i = Index(index,local_store=config.config_path,endtime=target_date)
            i.get_tickers_list()
            i.compare_avg_ma(ma=50)
            notify_message += f"{i.gen_index_msg()}\n"
            admin_message += i.err_msg

        # 计算两市成交量与昨日的变化
        print("计算两市成交量与昨日的变化")
        for index in ['nasdaq','nyse']:
            print(f"{index}")
            i = Index(index,from_s="markets",local_store=config.config_path,endtime=target_date)
            i.compare_market_volume(debug=True)
            notify_message += f"{i.market_volume_msg}"
            admin_message += i.err_msg
        
        if notify_message:
            notify_message = f"🌈🌈🌈{target_date}天相🌈🌈🌈: \n\n{notify_message}\n{ENV.CONTRIBUTORS}"
            sendmsg(bot,notifychat,notify_message,debug)
        if admin_message:
            sendmsg(bot,adminchat,admin_message,debug)
    except Exception as err:
        sendmsg(bot,adminchat,f"今天完蛋了，什么都不知道，快去通知管理员，bot已经废物了，出的问题是:\n{type(err)}:\n{err}",debug)
        raise err