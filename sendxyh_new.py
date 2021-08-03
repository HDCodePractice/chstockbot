import getopt,sys,config,os
import datetime
from telegram import Bot
from stockutil import stooq, wikipedia
from stockutil.ticker import Ticker,sendmsg

target_date = datetime.date.today()

def help():
    return "sendxyh.py -c configpath -d yyyymmdd"

def get_spx_ndx_avg_msg(ma=50,end=datetime.date.today()):
    """
    获取spx和ndx在50MA之上的股票数量的百分比信息，返回发给用户的信息。
    """
    msg = ""
    err_msg =""
    sp500 = wikipedia.get_sp500_tickers()
    ndx100 = wikipedia.get_ndx100_tickers()
    indexes = {"SPX": sp500, "NDX": ndx100}
    # indexes = {"ndx100": ndx100}
    for key in indexes:
        up = []
        down = []       
        for symbol in indexes[key]:
            try:
                if stooq.symbol_above_moving_average(symbol,ma=ma,path=f"{config.config_path}/data",end=end): 
                    up.append(symbol)
                else:
                    down.append(symbol)
            except stooq.markCloseError:
                err_msg += f"{key}: {symbol} {end.strftime('%Y-%m-%d')}没有数据\n"
                #break 移除break 防止出现只有部分ticker没有数据但是大部分有数据的情况
            except Exception as e:
                err_msg += f"unreachable stock: {symbol}\nerror message: {e}\n"
        if down:
            msg += f"{key}共有{len(up)+len(down)}支股票，共有{len(up)/(len(up)+len(down))*100:.2f}%高于{ma}周期均线\n"
        if len(up)+len(down) + 20 < len(indexes[key]):
            err_msg = f"{key}: {end.strftime('%Y-%m-%d')} 有超过20支股票没有数据，请确保输入的日期当天有开市\n"
    return msg, err_msg


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
    msg,err  = get_spx_ndx_avg_msg(end=target_date)
    notify_message += msg
    admin_message += err
    try:
        for datasource in ds:
            for symbol in symbols:
                ticker = Ticker(symbol[0])
                ticker.source = datasource
                ticker.endtime = target_date
                ticker.load_web_data()
                ticker.cal_symbols_avg(symbol[1:])
                admin_message += ticker.admin_msg
                notify_message += ticker.xyh_msg
            break
        if admin_message:
            sendmsg(bot,adminchat,admin_message,debug=debug)
        if ticker.xyh_msg:
            notify_message = f"🌈🌈🌈{target_date}天相🌈🌈🌈: \n\n{notify_message}\n贡献者:毛票教的大朋友们"
            sendmsg(bot,notifychat,notify_message,debug=debug)
    except Exception as err:
        sendmsg(bot,adminchat,f"今天完蛋了，什么都不知道，快去通知管理员，bot已经废物了，出的问题是:\n{type(err)}:\n{err}",debug)
    
    