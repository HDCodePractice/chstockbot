import getopt,sys,config,os
import pandas_datareader.data as web
import datetime
from telegram import Bot
from pandas_datareader._utils import RemoteDataError



symbols = [["SPY",10,50]]
ds = 'yahoo'
notifychat = -1001430794202
adminchat = -1001430794202
# symbols = [["SPY",10,50]]

def help():
    return "'sendxyh.py -c configpaht'"

def cal_symbols_avg(ds:str, symbol:str, avgs:list):
    start = datetime.date.today() - datetime.timedelta(days=365)
    end = datetime.date.today()
    try:
        df = web.DataReader(symbol.upper(), ds,start=start,end=end).sort_values(by="Date")
        if datetime.date.today() == df.index.date[-1]: #做了一个checkpoint来查找今天的数据; credit for Stephen
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
            return f"{message}\n"
        else:
            return f"{ds} 没找到今天的数据，看来要不没开市，要不没收盘，先不发天相了\n"
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

    message = "🌈🌈🌈当日天相🌈🌈🌈: \n"
    try:
        for symbol in symbols: 
            message += cal_symbols_avg(ds,symbol[0],symbol[1:])
        if not "先不发天相了" in message:
            bot.send_message(notifychat,message)
            #bot.send_message(adminchat,f"向{notifychat}发送成功夕阳红:\n{message}")
        else:
            bot.send_message(adminchat,f"Admin Group Message: {ds} 数据源没找到今天的数据，看来要不没开市，要不没收盘，先不发天相了，请4点后重新尝试")
    except Exception as err:
        print(err)
        bot.send_message(adminchat,f"今天完蛋了，什么都不知道，快去通知管理员，bot已经废物了，出的问题是:\n{type(err)}:\n{err}")