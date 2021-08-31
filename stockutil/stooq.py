import datetime  
import pandas as pd
import datetime
import requests
import os
import pathlib
from zipfile import ZipFile

class markCloseError(Exception):
    pass

class maNotEnoughError(Exception):
    pass

def read_stooq_file(path="~/Downloads/data/daily/us/nasdaq stocks/3/tlry.us.txt"):
    """
    适配 Yahoo 格式

    Parameters
    ----------
    path: 读取stooq的文件路径

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

def search_file(rule=".txt", path='.')->list:
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
            if filename.endswith("/" + rule):  # 判断是否是"xxx"结尾
                all.append(filename)
    return all

def list_file_prefix(include_path,rule="*.txt", path='data/', )->list:
    """
    在path目录下搜索结尾名为rule的所有文件。返回：所有结尾名为rule的文件路径列表
    include_path：将指定目录下的文件去除
    Parameters
    ----------
    rule : 后缀
    path : 搜索路径。default为当前目录(".")
    include_path: 指定目录
    """
    all = []
    for fpathe,dirs,fs in os.walk(path):   # os.walk是获取所有的目录
        if include_path in fpathe:
            for f in fs:
                if f.endswith(rule):  # 判断是否是"xxx"结尾
                    all.append(f.split(".us.txt")[0].upper())
    return all


def symbol_above_moving_average(symbol:str,ma=50,path="~/Downloads/data",end=datetime.date.today())->bool:
    """
    TODO: 这个代码将会挪去Ticker类里
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
    tiker_file = search_file(symbol.lower().replace(".","-") + ".us.txt",os.path.expanduser(path))
    df = read_stooq_file(path=tiker_file[0])
    #filter df based on end time
    if end in df.index.date:
        df = df.loc[df.index[0]:end]
        if df.count()[0] > ma :
            if df['Adj Close'][-1] < df.tail(ma)['Adj Close'].mean():
                return False
            else:
                return True
        else:
            raise maNotEnoughError(f"{ma} 周期均价因时长不足无法得出\n")
    else:
        raise markCloseError(f"输入的日期没有数据，请确保输入的日期当天有开市\n")



if __name__ == '__main__':
    tiker_file = search_file("atvi.us.txt",os.path.expanduser("~/Downloads/data"))
    print(read_stooq_file(path=tiker_file[0]))
    # for ticker in sp500:
    #     msg = 0
    #     try:
    #         if symbol_above_moving_average("ticker",50,path="~/Downloads/data",end=datetime.date(2021,7,2)):
    #             msg += 1
    #     except maNotEnoughError as err:
    #         print(err)
    #     except markCloseError as err:
    #         print(err)
