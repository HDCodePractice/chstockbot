import getopt,sys,config,os
import pandas_datareader.data as web
import datetime
from telegram import Bot
from pandas_datareader._utils import RemoteDataError

symbols = [["SPY",10,50],["QQQ",13,55,200],["RBLX",13,55,200]]
ds = 'stooq'
notifychat = -1001430794202
adminchat = -1001250988031
# symbols = [["SPY",10,50]]

def help():
    return "'sendxyh.py -c configpath'"

def cal_symbols_avg_stooq(symbol:str,avgs:list):
    pass

def cal_symbols_avg_yahoo(symbol:str,avgs:list):
    start = datetime.date.today() - datetime.timedelta(days=365)
    end = datetime.date.today()

    try:
        df = web.DataReader(symbol.upper(), 'yahoo',start=start,end=end)
        message = f"{symbol.upper()}价格: {df['Close'][-1]:0.2f}({df['Low'][-1]:0.2f} - {df['High'][-1]:0.2f}) \n"
        for avg in avgs:
            if df.count()[0] > avg :
                message += f"{avg} 周期均价：{df.tail(avg)['Adj Close'].mean():0.2f}\n"
            else:
                message += f"{avg} 周期均价因时长不足无法得出\n"
        return f"{message}\n"
    except RemoteDataError:
        return f"{symbol}丢失了\n"

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

    message = "🌈🌈🌈当日天相🌈🌈🌈: \n"
    try:
        for symbol in symbols:
            message += cal_symbols_avg_yahoo(symbol[0],symbol[1:])
        message += "贡献者:毛票教的大朋友们"
        bot.send_message(notifychat,message)
        # bot.send_message(adminchat,f"向{notifychat}发送成功夕阳红:\n{message}")
    except Exception as err:
        print(err)
        bot.send_message(adminchat,f"今天完蛋了，什么都不知道，快去通知管理员，bot已经废物了出的问题是:\n{type(err)}:\n{err}")