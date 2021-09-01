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

