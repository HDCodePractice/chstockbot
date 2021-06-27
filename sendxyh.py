import getopt,sys,config,os
import pandas_datareader.data as web
import datetime
from telegram import Bot

def help():
    return "'sendxyh.py -c configpath'"

def cal_symbols_avg(ds:list, symbol:str, avgs:list,end=datetime.date.today()):
    start = end - datetime.timedelta(days=365)
    for datasource in ds:
        try:
            df = web.DataReader(symbol.upper(), datasource,start=start,end=end)
            df = df.sort_values(by="Date") #将排序这个步骤放在了判断df是否存在之后
            if "Adj Close" in df.columns.values: #把df的cloumn名字改掉, 防止名字冲突
                df = df.rename(columns={"Close":"Close Backup","Adj Close": "Close"})
            if end == df.index.date[-1]: #做了一个checkpoint来查找今天的数据; credit for Stephen
                message = f"{symbol.upper()}价格: {df['Close'][-1]:0.2f}({df['Low'][-1]:0.2f} - {df['High'][-1]:0.2f}) \n"
                for avg in avgs:
                    if df.count()[0] > avg :
                        #加入红绿灯的判断
                        if df['Close'][-1] < df.tail(avg)['Close'].mean():
                            flag = "🔴"
                        else:
                            flag = "🟢"
                        message += f"{flag} {avg} 周期均价：{df.tail(avg)['Close'].mean():0.2f}\n"
                    else:
                        message += f"{avg} 周期均价因时长不足无法得出\n"  
                return True, f"{message}\n"       
            else: #当天不是交易日时 返回false
                return 2, f"今天不是交易日，不需要发送信息\n"
        except Exception as e: 
            if datasource == ds[-1]:
                return False, f"{e}\n"
            continue

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
            output = cal_symbols_avg(ds,symbol[0],symbol[1:])
            if output[0] == True:
                notify_message += output[1] 
            elif output[0] == False:
                 admin_message +=output[1]
            else:
                print(f"{adminchat}\n今天不是交易日，不发送信息")
                sys.exit("今天不是交易日，不发送信息，终止当前程序")
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
