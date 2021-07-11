import datetime  
import pandas as pd
import datetime
import requests
import os
from zipfile import ZipFile

class markCloseError(Exception):
    pass

class maNotEnoughError(Exception):
    pass

def download_file(url="https://static.stooq.com/db/h/d_us_txt.zip",dict="~/Downloads"):
    msg = ""
    err = ""
    try:
        request = requests.get(url)
        if not os.path.exits(os.path.expanduser(dict)):
            os.makedirs(os.path.expanduser(dict))
        with open(os.path.expanduser(f"{dict}/{url.split('/')[-1]}"), 'wb') as f:
            f.write(request.content)
        f.close

        zf = ZipFile(os.path.expanduser(f"{dict}/{url.split('/')[-1]}"), 'r')
        zf.extractall(os.path.expanduser(dict))
        zf.close()
        msg += f"下载和解压成功"
    # 网站服务器当机无法下载 用Exception解决
    # 解压文件受损，无法解压 用Exception解决
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

def symbol_above_moving_average(symbol:str,ma=50,path="~/Downloads/data",end=datetime.date.today())->bool:
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
    err_msg = ""
    successful_msg = ""
    tiker_file = search_file(symbol.lower() + ".us.txt",os.path.expanduser(path))
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
    print(download_file())
    # for ticker in sp500:
    #     msg = 0
    #     try:
    #         if symbol_above_moving_average("ticker",50,path="~/Downloads/data",end=datetime.date(2021,7,2)):
    #             msg += 1
    #     except maNotEnoughError as err:
    #         print(err)
    #     except markCloseError as err:
    #         print(err)
