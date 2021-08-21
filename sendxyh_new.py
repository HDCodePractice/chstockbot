import getopt,sys,config,os
import datetime
from telegram import Bot
from stockutil import stooq, wikipedia
from stockutil.ticker import Ticker
from util.utils import sendmsg
from stockutil.index import Index
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

    bot = Bot(token = CONFIG['Token'])
    symbols = CONFIG['xyhticker']
    notifychat = CONFIG['xyhchat']
    adminchat = CONFIG['xyhlog']
    debug = CONFIG['DEBUG']
    ds = CONFIG['xyhsource']    

    notify_message = ""
    admin_message = ""
    #msg,err  = get_spx_ndx_avg_msg(end=target_date)
    #admin_message += err
    xyh_msg = ""
    msg  = ""
    try:
        for symbol,value in Index.sources.items():
            index = Index(symbol)
            symbol= index.get_index_tickers_list()
            data = index.compare_avg(ma=50,end_date=target_date)
            if data['up_num']+data['down_num'] + 20 < len(index.tickers):
                admin_message += f"{index.symbol}: {target_date.strftime('%Y-%m-%d')} 有超过20支股票没有数据，请确保输入的日期当天有开市\n"
            else:
                msg += f"{index.symbol}共有{data['up_num']+data['down_num']}支股票，共有{data['rate']*100:.2f}%高于{index.ma}周期均线\n"
        for datasource in ds:
            for symbol in symbols:
                ticker = Ticker(symbol[0],"web",datasource,endtime=target_date)
                ticker.load_data()
                xyh_msg += f"{ticker.symbol}价格: {ticker.df['Close'][-1]}({ticker.df['Low'][-1]} - {ticker.df['High'][-1]}):\n"
                for ma in symbol[1:]:
                    ticker.cal_symbols_avg(ma)
                    ticker.cal_sams_change_rate()
                xyh_msg += f"{ticker.gen_xyh_msg()}\n"

            break
    except Exception as err:
        sendmsg(bot,adminchat,f"今天完蛋了，什么都不知道，快去通知管理员，bot已经废物了，出的问题是:\n{type(err)}:\n{err}",debug)
    
    if xyh_msg:
        notify_message += f"🌈🌈🌈{target_date}天相🌈🌈🌈: \n\n{xyh_msg}\n{msg}\n贡献者:毛票教的大朋友们\n"
        sendmsg(bot,notifychat,notify_message,debug=debug)
    if admin_message:
        sendmsg(bot,adminchat,admin_message,debug=debug)
    

    