import getopt,sys,config,os
from requests.sessions import extract_cookies_to_jar
import pandas_datareader.data as web
import datetime
from telegram import Bot
from pandas_datareader._utils import RemoteDataError
from requests.exceptions import ConnectionError
from stockutil import stooq, wikipedia

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

def cal_symbols_avg(ds:list, symbol:str, avgs:list,end=datetime.date.today()):
    start = end - datetime.timedelta(days=365)
    successful_msg = ""
    err_msg = ""
    for datasource in ds:
        try:
            df = web.DataReader(symbol.upper(), datasource,start=start,end=end)
            df = df.sort_values(by="Date") #将排序这个步骤放在了判断df是否存在之后
            if "Adj Close" not in df.columns.values: #当数据没有adj close时，从close 数据copy给adj close
                df["Adj Close"] = df["Close"]
            if end == df.index.date[-1]: #做了一个checkpoint来查找今天的数据; credit for Stephen
                successful_msg += f"{symbol.upper()}价格: {df['Adj Close'][-1]:0.2f}({df['Low'][-1]:0.2f} - {df['High'][-1]:0.2f}) \n"
                for avg in avgs:
                    if df.count()[0] > avg :
                        #加入红绿灯的判断
                        if df['Adj Close'][-1] < df.tail(avg)['Adj Close'].mean():
                            flag = "🔴"
                        else:
                            flag = "🟢"
                        percentage = (df['Adj Close'][-1] - df.tail(avg)['Adj Close'].mean())/df.tail(avg)['Adj Close'].mean() * 100
                        successful_msg += f"{flag} {avg} 周期均价：{df.tail(avg)['Adj Close'].mean():0.2f} ({percentage:0.2f}%)\n"
                    else:
                        successful_msg += f"{avg} 周期均价因时长不足无法得出\n"         
            else: #当天不是交易日时 返回false
                err_msg += f"今天不是交易日，不需要发送{symbol}信息\n"
            break #当数据源成功读取并处理数据后，从当前程序break并返回信息； 防止程序运行所有的数据源
        except NotImplementedError:
            err_msg += f"当前数据源{datasource}不可用"
            continue
        except RemoteDataError:
            err_msg += f"在{datasource}找不到{symbol}的信息\n"
            continue
        except Exception as e: 
            err_msg += f"当前{symbol}读取报错了，具体错误信息是{e}\n"
            continue
    return successful_msg, err_msg

def sendmsg(bot,chatid,msg,debug=True):
    if debug:
        print(f"{chatid}\n{msg}")
    else:
        bot.send_message(chatid,msg)

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
   

    notify_message = ""
    admin_message = ""

    try:
        for symbol in symbols:
            successful_msg, err_msg = cal_symbols_avg(ds,symbol[0],symbol[1:],end=target_date)#debug的end变量需要被删除: ,end=datetime.date(2021,7,1)
            if successful_msg:
                notify_message += f"{successful_msg}\n"
            if err_msg:
                admin_message += err_msg
        msg,err  = get_spx_ndx_avg_msg(end=target_date)
        if err:
            admin_message += err
        if notify_message:
            notify_message = f"🌈🌈🌈{target_date}天相🌈🌈🌈: \n\n{notify_message}\n{msg}\n贡献者:毛票教的大朋友们"
            sendmsg(bot,notifychat,notify_message,debug)
        if admin_message:
            sendmsg(bot,adminchat,admin_message,debug)
    except Exception as err:
        sendmsg(bot,adminchat,f"今天完蛋了，什么都不知道，快去通知管理员，bot已经废物了，出的问题是:\n{type(err)}:\n{err}",debug)