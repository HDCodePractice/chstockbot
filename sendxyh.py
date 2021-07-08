import getopt,sys,config,os
import pandas_datareader.data as web
import datetime
from telegram import Bot
from pandas_datareader._utils import RemoteDataError
from requests.exceptions import ConnectionError
from stockutil import stooq



def help():
    return "'sendxyh.py -c configpath'"

def get_spx_ndx_avg_msg():
    """
    获取spx和ndx在50MA之上的股票数量的百分比信息，返回发给用户的信息。
    """
    return ""

def cal_symbols_avg(ds:list, symbol:str, avgs:list,end=datetime.date.today()):
    start = end - datetime.timedelta(days=365)
    successful_msg = ""
    err_msg = ""
    for datasource in ds:
        try:
            df = web.DataReader(symbol.upper(), datasource,start=start,end=end)
            df = df.sort_values(by="Date") #将排序这个步骤放在了判断df是否存在之后
            if "Adj Close" in df.columns.values: #把df的cloumn名字改掉, 防止名字冲突
                df = df.rename(columns={"Close":"Close Backup","Adj Close": "Close"})
            if end == df.index.date[-1]: #做了一个checkpoint来查找今天的数据; credit for Stephen
                successful_msg += f"{symbol.upper()}价格: {df['Close'][-1]:0.2f}({df['Low'][-1]:0.2f} - {df['High'][-1]:0.2f}) \n"
                for avg in avgs:
                    if df.count()[0] > avg :
                        #加入红绿灯的判断
                        if df['Close'][-1] < df.tail(avg)['Close'].mean():
                            flag = "🔴"
                            percent = '-{:.2%}'.format(1-df['Close'][-1]/df.tail(avg)['Close'].mean())
                        else:
                            flag = "🟢"
                            percent = '{:.2%}'.format(df['Close'][-1]/df.tail(avg)['Close'].mean()-1)
                        successful_msg += f"{flag} {avg} 周期均价：{df.tail(avg)['Close'].mean():0.2f}({percent})\n"
                    else:
                        successful_msg += f"{avg} 周期均价因时长不足无法得出\n"         
            else: #当天不是交易日时 返回false
                err_msg += f"今天不是交易日，不需要发送{symbol}信息\n"
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

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:", ["config="])
    except getopt.GetoptError:
        print(help())
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(help())
            sys.exit()
        elif opt in ("-c", "--config"):
            config.config_path = arg          

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
    try:
        for symbol in symbols:
            successful_msg, err_msg = cal_symbols_avg(ds,symbol[0],symbol[1:],datetime.date(2021,7,2))
            if successful_msg:
                notify_message += successful_msg
            if err_msg:
                admin_message += err_msg
        if debug :
            if notify_message:
                notify_message = "🌈🌈🌈当日天相🌈🌈🌈: \n" + notify_message + "贡献者:毛票教的大朋友们"
                print(f"{notifychat}\n{notify_message}")
            if admin_message:
                print(f"{adminchat}\n{admin_message}")
        else:
            if notify_message:
                notify_message = "🌈🌈🌈当日天相🌈🌈🌈: \n" + notify_message + "贡献者:毛票教的大朋友们"
                bot.send_message(notifychat,notify_message)
            if admin_message:
                bot.send_message(adminchat,admin_message)
    except Exception as err:
        if debug:
            print(f"{adminchat}\n今天完蛋了，什么都不知道，快去通知管理员，bot已经废物了，出的问题是:\n{type(err)}:\n{err}")
        else:
            bot.send_message(adminchat,f"今天完蛋了，什么都不知道，快去通知管理员，bot已经废物了，出的问题是:\n{type(err)}:\n{err}")
