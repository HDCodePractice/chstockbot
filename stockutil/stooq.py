import pandas as pd
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

def search_file( rule=".txt", path='.'):
    all = []
    for fpathe,dirs,fs in os.walk(path):   # os.walk是获取所有的目录
        for f in fs:
            filename = os.path.join(fpathe,f)
            if filename.endswith(rule):  # 判断是否是"xxx"结尾
                all.append(filename)
    return all

def symbol_above_moving_average(symbol,avg):
    return True


if __name__ == '__main__':
    tiker_file = search_file("tlry.us.txt",os.path.expanduser("~/Downloads/data"))
    print(read_stooq_file(path=tiker_file[0]))