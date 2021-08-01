import pandas_datareader.data as web
import datetime

class TickerError(Exception):
    pass

class Ticker:
    symbol = None
    data = None
    end_date = None
    # Ticker的SMA及对应的值
    smas = {}
    # Ticker的SMA所对应的状态[change_rate,flag]
    smas_state = {}


    def __init__(self, symbol, end_date=datetime.date.today()):
        self.symbol = symbol
        self.end_date = end_date

    def load_data_by_web(self,source="stooq"):
        symbol = self.symbol
        self.data = None
        df = web.DataReader(symbol.upper(),source,end=self.end_date)
        df = df.sort_values(by="Date")
        if "Adj Close" not in df.columns.values: #当数据没有adj close时，从close 数据copy给adj close
                df["Adj Close"] = df["Close"]
        self.data = df
        self.clena_sma()
        return self.data

    def append_sma(self,ma=10):
        # 数据没加载
        if self.data is None:
            self.load_data_by_web()
        
        df = self.data
        
        if df.count()[0] < ma :
            raise TickerError(f"{self.symbol}里的历史数据没有{ma}这么多")

        if self.end_date != df.index.date[-1]:
            raise TickerError(f"{self.symbol}最后一个交易日不是{self.end_date}")

        sma = df.tail(ma)['Adj Close'].mean()
        self.smas[ma] = sma
        return sma

    def cal_sams_change_rate(self):
        df = self.data
        for ma,value in self.smas.items():
            percentage = (df['Adj Close'][-1] - value)/value * 100
            self.smas_state[ma] = [percentage, "🟢" if percentage > 0 else "🔴"]
        return self.smas_state

    def clena_sma(self):
        self.smas = {}
        self.smas_state = {}


class INDEX:
    symbol = None
    # 得到INDEX的成分股
    # 成份股高于MA的数量和比例
    pass

if __name__ == "__main__":
    tickers = ["spy","qqq","didi"]
    admin_msg = ""
    notify_msg = ""

    for ticker in tickers:
        try:
            a = Ticker(ticker,datetime.date(2021,7,30))
            a.load_data_by_web()
            a.append_sma(10)
            a.append_sma(50)
            a.append_sma(100)
            a.append_sma(200)
            a.cal_sams_change_rate()
            notify_msg += f"{a.smas} {a.smas_state}"
        except TickerError as e:
            admin_msg += str(e)
    print("=================================")
    print(admin_msg)
    print("=================================")
    print(notify_msg)