from typing import List
import pandas as pd
import datetime
import os

def read_stooq_file(path="~/Downloads/data/daily/us/nasdaq stocks/2/tlry.us.txt"):
    """
    适配 Yahoo 格式
    """
    df = pd.read_csv(path, parse_dates=True)
    df = df.rename(columns={
        '<OPEN>': 'Open',
        '<CLOSE>': 'Adj Close',
        '<HIGH>': 'High',
        '<LOW>': 'Low',
        '<VOL>': 'Volume',
        '<DATE>': 'Date',
    })

    df = pd.DataFrame(df[['Date', 'Open', 'Adj Close', 'High', 'Low', 'Volume']])
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
    df.set_index('Date', inplace=True)
    df['Close'] = df['Adj Close']

    return df

def search_file(rule=".txt", path='.')->List:
    """
    在path目录下搜索结尾名为rule的所有文件。返回：所有结尾名为rule的文件路径列表

    Parameters
    ----------
    rule : 后缀
    path : 搜索路径。default为当前目录(".")
    """
    all = []
    for fpathe,dirs,fs in os.walk(path):   # os.walk是获取所有的目录
        for f in fs:
            filename = os.path.join(fpathe,f)
            if filename.endswith(rule):  # 判断是否是"xxx"结尾
                all.append(filename)
    return all

def symbol_above_moving_average(symbol:str,filepath:str,avg:int=50,end=datetime.date.today()):
    """
    获取一个股票代码是否高于指定的历史平均价。返回True高于avg，Flase低于avg

    Parameters
    ----------
    symbol : str
        股票代码
    filepath : str
        stooq离线文件存储的目录路径
    avg : int, default 50
        计算的历史时长，默认为50MA
    end : datetime.date, default today
        计算到的截止日期，默认为当天
    """
    symbolfile = search_file(rule=f"{symbol.lower()}.us.txt",path=filepath)[0]
    df = read_stooq_file(path=symbolfile)
    if df['Adj Close'][-1] < df.tail(avg)['Adj Close'].mean():
        return True
    return False

if __name__ == '__main__':
    tiker_file = search_file("qqq.us.txt",os.path.expanduser("~/Downloads/data"))
    print(tiker_file)
    print(read_stooq_file(path=tiker_file[0]))
    print(symbol_above_moving_average("qqq","/Users/hd/Downloads/data/daily/us"))