import getopt,sys,config,os
import pandas_datareader.data as web
import datetime
from telegram import Bot
from pandas_datareader._utils import RemoteDataError 

notifychat = -1001430794202
adminchat = -1001250988031
ds = ['stooq','yahoo']
symbols = [["SPY",10,50]]
avgs = [10, 50]

#def cal_symbols_avg_stooq(symbol:str,avgs:list):
start = datetime.date.today() - datetime.timedelta(days=365)
end = datetime.date.today()
now = datetime.datetime.now()
#today = datetime.date.today()
df = web.DataReader('spy', ds[0], start=start,end=end)

print (now.strftime('%Y-%m-%d'))
print (df.index.date[0])

if now.strftime('%Y-%m-%d') == df.index.date[0]:
    try:
        message = f"spy价格: {df['Close'][0]:0.2f}({df['Low'][0]:0.2f} - {df['High'][0]:0.2f}) \n"
        for avg in avgs:
            if df.count()[0] > avg :
                if f"{df['Close'][0]:0.2f}" > f"{df.head(avg)['Close'].mean():0.2f}":
                    message += f"🟢{avg} 周期均价：{df.head(avg)['Close'].mean():0.2f}\n"
                else:
                    message += f"🔴{avg} 周期均价：{df.head(avg)['Close'].mean():0.2f}\n"
            else:
                message += f"{avg} 周期均价因时长不足无法得出\n"
        print (f"{message}\n")
    except RemoteDataError:
        #return f"spy丢失了\n"
        print( f"spy丢失了\n")
else:
    message = f"现在是 {now}， 不是交易时间哦，休息一下吧。\n"
    print (message)
