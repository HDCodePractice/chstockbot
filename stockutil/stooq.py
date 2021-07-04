import datetime
import time
import pandas as pd
import datetime
import requests
import os
from zipfile import ZipFile

def download_file(url="https://static.stooq.com/db/h/d_us_txt.zip",dict="~/Downloads/d_us_txt.zip"):
    msg = ""
    err = ""
    try:
        request = requests.get(url)
        with open(os.path.expanduser(dict), 'wb') as f:
            f.write(request.content)
        f.close

        zf = ZipFile(os.path.expanduser(dict), 'r')
        zf.extractall(os.path.expanduser('~/Downloads'))
        zf.close()
        msg += f"下载和解压成功"
    except Exception as e:
        err += f"下载和解压出错了；具体错误是：{e}"
    return msg,err

def check_stock_data(path="~/Downloads/data/daily/us/nasdaq stocks/3/tlry.us.txt"):
    now = datetime.date.today()
    msg = ""
    err = ""
    try:#verify creation time of the data
        if os.path.exists(os.path.expanduser(path)):
            stat = os.path.getmtime(os.path.expanduser(path))
            if datetime.datetime.fromtimestamp(stat).date() == now:
                msg += "数据是最新的，不需要下载"
            else:#download file and unzip it
                dl_msg,dl_err = download_file()
                msg += dl_msg
                err += dl_err
        else:
            dl_msg,dl_err = download_file()
            msg += dl_msg
            err += dl_err
        msg += "数据比较完成"    
    except Exception as e:
        err += f"{e}"
    return msg, err

def read_stooq_file(path="~/Downloads/data/daily/us/nasdaq stocks/3/tlry.us.txt"):
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

def search_file( rule=".txt", path='.'):
    all = []
    for fpathe,dirs,fs in os.walk(path):   # os.walk是获取所有的目录
        for f in fs:
            filename = os.path.join(fpathe,f)
            if filename.endswith("/" + rule):  # 判断是否是"xxx"结尾
                all.append(filename)
    return all

def symbol_above_moving_average(symbol,avg=50,end=datetime.date.today()):
    """
    获取一个股票代码是否高于指定的历史平均价。

    Parameters
    ----------
    symbol : str
        股票代码
    avg : int, default 50
        计算的历史时长，默认为50MA
    end : datetime.date, default today
        计算到的截止日期，默认为当天
    """
    return True


def compare_avg_price(symbol,ma=50,end=datetime.date.today()):
    msg,err = check_stock_data()
    err_msg = ""
    successful_msg = ""
    if msg:
        tiker_file = search_file(symbol.lower() + ".us.txt",os.path.expanduser("~/Downloads/data"))
        df = read_stooq_file(path=tiker_file[0])
        #filter df based on end time
        if end in df.index.date:
            df = df.loc[df.index[0]:end]
            if df.count()[0] > ma :
                if df['Adj Close'][-1] < df.tail(ma)['Adj Close'].mean():
                    successful_msg += f"🔴 {ma}均价: {df.tail(ma)['Adj Close'].mean():.2f} {end}当天收盘价：{df['Adj Close'][-1]:.2f}\n"
                else:
                    successful_msg += f"🟢 {ma}均价: {df.tail(ma)['Adj Close'].mean():.2f} {end}当天收盘价：{df['Adj Close'][-1]:.2f}\n"
            else:
                err_msg += f"{ma} 周期均价因时长不足无法得出\n"
        else:
            err_msg += f"输入的日期没有数据，请确保输入的日期当天有开市\n"
    if err:
        err_msg += f"数据出错了，具体信息如下:{err}\n"
    return successful_msg,err_msg
    #calculate ma price
    


if __name__ == '__main__':
    #tiker_file = search_file("tlry.us.txt",os.path.expanduser("~/Downloads/data"))
    #print(read_stooq_file(path=tiker_file[0]))
    #print(download_file())
    print(compare_avg_price("qqq",50,end=datetime.date(2021,6,16)))
