import pandas as pd
import pandas_datareader.data as web
import datetime

class TickerError(Exception):
    pass

class Ticker:
    symbol = None
    data = None
    start_date = None
    end_date = None
    smas = {}
    smas_state ={}

    def __init__(self, symbol, end_date = datetime.date.today()):
        self.symbol = symbol
        self.end_date = end_date

    def load_web_data(self, source = 'stooq'):
        symbol = self.symbol
        self.data = None
        df = web.DataReader(self.symbol.upper(), source, end = self.end_date)
        df = df.sort_values(by="Date")
        if "Adj Close" not in df.columns.values: #当数据没有adj close时，从close 数据copy给adj close
                df["Adj Close"] = df["Close"] 
        self.data = df
        return self.data

    def append_sma(self,ma=10):
        # 数据没加载
        if self.data is None:
            self.load_data_by_web()
        
        df = self.data
        
        if df.count()[0] < ma :
            raise TickerError(f"Ticker里的历史数据没有{ma}这么多")

        if self.end_date != df.index.date[-1]:
            raise TickerError(f"最后一个交易日不是{self.end_date}")

        sma = df.tail(ma)['Adj Close'].mean()
        self.smas[ma] = sma
        return sma


    def cal_sams_change_rate(self):
        if self.data is None:
            self.load_data_by_web()
        df = self.data

        if self.smas is None:
            for ma,value in self.smas.items():
                percentage = (df['Adj Close'][-1] - value)/value * 100
                flag = "🟢" if percentage > 0 else "🔴"
                self.smas_state[ma] = [percentage,"🟢"]
            #self.smas_state[ma] = [percentage, "🟢" if percentage > 0 else "🔴"]
        return self.smas_state

# symbols = ["aapl","tsla","tlry"]

# for symbol in symbols:
#     price_info = Ticker(symbol)
#     latest_price = price_info.load_web_data()['Adj Close'][-1]
#     print (latest_price)


a = Ticker("aapl", datetime.date(2021,7,29))
a.load_web_data()
a.append_sma(10)
a.append_sma(20)
a.append_sma(50)
print (a.cal_sams_change_rate()) 



# import pandas_datareader.data as web
# import datetime

# class TickerError(Exception):
#     pass

# class Ticker:
#     symbol = None
#     data = None
#     end_date = None

#     def __init__(self, symbol, end_date=datetime.date.today()):
#         self.symbol = symbol
#         self.end_date = end_date

#     def load_data_by_web(self,source="stooq"):
#         symbol = self.symbol
#         self.data = None
#         df = web.DataReader(symbol.upper(),source,end=self.end_date)
#         df = df.sort_values(by="Date")
#         if "Adj Close" not in df.columns.values: #当数据没有adj close时，从close 数据copy给adj close
#                 df["Adj Close"] = df["Close"]
#         self.data = df
#         return self.data

#     def cal_sma(self,ma=10):
#         # 数据没加载
#         if self.data is None:
#             self.load_data_by_web()
        
#         df = self.data
        
#         if df.count()[0] < ma :
#             raise TickerError(f"Ticker里的历史数据没有{ma}这么多")

#         if self.end_date != df.index.date[-1]:
#             raise TickerError(f"最后一个交易日不是{self.end_date}")

#         sma = df.tail(ma)['Adj Close'].mean()
#         return sma

# a = Ticker("aapl",datetime.date(2021,7,1))
# a.load_data_by_web()
# print(a.cal_sma(50))
# print(a.cal_sma(2000))
