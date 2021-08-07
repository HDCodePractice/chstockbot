from numpy import ndindex
import pandas_datareader.data as web
import pandas as pd
import datetime
import os

class TickerError(Exception):
    pass

def get_week_num(year, month, day):
    """
    获取当前日期是本月的第几周
    """
    start = int(datetime.date(year, month, 1).strftime("%W"))
    end = int(datetime.date(year, month,day).strftime("%W"))
    week_num = end - start + 1
    return week_num

class Ticker:
    symbol = None
    data = None
    end_date = None
    # Ticker的SMA及对应的值
    smas = {}
    # Ticker的SMA所对应的状态[change_rate,flag]
    smas_state = {}
    price_lists = {}

    def __init__(self, symbol, end_date=datetime.date.today()):
        self.symbol = symbol
        self.end_date = end_date

    def load_data(self,source):
        """
        从本地或某特定路径或stooq取得ticker的数据。
        """
        symbol = self.symbol
        self.data = None
        if source == "stooq":
            df = web.DataReader(symbol.upper(),source,end=self.end_date)
            df = df.sort_values(by="Date")
            if "Adj Close" not in df.columns.values: #当数据没有adj close时，从close 数据copy给adj close
                    df["Adj Close"] = df["Close"]
            self.data = df
            self.clean_sma()
        else:
            ticker_file = stooq.search_file(symbol.lower().replace(".","-") + ".us.txt",os.path.expanduser(source))
            df = stooq.read_stooq_file(path = ticker_file[0])
            self.data = df
            self.clean_sma
            self.clean_price_lists
        return self.data

    def get_price_lists(self,start,end,freq='W-WED',week_num =2): 
        """
        获得某段时间内的特定日子的价格数据，此处为周三
        """
        end =self.end_date
        self.price_lists = None
        price_lists = {}
        if self.data is None:
            self.load_data()
        df = self.data
        date_list = pd.date_range(start=start, end=end, freq='W-WED').strftime('%Y-%m-%d').tolist()
    #    print (date_list)
        df_w = []
        df_m = []
        for date in date_list:
            date = datetime.datetime.strptime(date, "%Y-%m-%d")
            df_w.append(df.loc[date, 'Close'])
            price_lists['weekly'] = df_w
            if get_week_num(date.year, date.month, date.day) == week_num:
                df_m.append(df.loc[date, 'Close'])
                price_lists['montly'] = df_m
        return price_lists   

    def cal_profit(self, ticker_price):
        """
        计算某ticker指定时间段的利润率。
        Parameters
        ----------
        ticker_price : 每个定投日的收盘价格列表。 
        """
        times = len(ticker_price)

        #每周投入金额一样(100块)
        stock_num = 0
        for i in range (times):    
            stock_num += 100/ticker_price[i]
        cost = 100 * times
        cur_value = stock_num * self.data['Close'][-1]
        profit = cur_value - cost
        rate = (profit/cost)*100
        return {'rate': f"{rate:.2f}%", 'cost':f"{cost:.2f}", 'value':f"{cur_value:.2f}"}


    def clean_price_lists(self):
        self.price_lists = {}

    def append_sma(self,ma=10):
        # 数据没加载
        if self.data is None:
            self.load_data()
        
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

    def clean_sma(self):
        self.smas = {}
        self.smas_state = {}


class Index:
    symbol = None
    # 得到INDEX的成分股
    # 成份股高于MA的数量和比例
    sp500 = []
    ndx100 = []
    
    def __init__(self) -> None:
        pass

    def get_sp500_tickers(self):
        self.clean_sp500()
        table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        df = table[0]
        self.sp500 = df['Symbol'].tolist()
        return self.sp500

    def get_ndx100_tickers(self):
        self.clean_ndx100
        table = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')
        df = table[3]
        self.ndx100 = df['Ticker'].tolist() 
        return self.ndx100

    def compare_avg(self, ma=50, index = ndx100, end_date=datetime.date.today()):
        up = []
        down = []
        avg_com_info = {}
        for symbol in index:
            symbol = Ticker(symbol,end_date= end_date)
            df = symbol.load_data()
            if df['Adj Close'][-1] < df.tail(ma)['Adj Close'].mean():
                up.append(symbol)
            else:
                down.append(symbol)     
        avg_com_info['up_num'] = len(up)
        avg_com_info['up_rate'] = len(up)/(len(up)+len(down))
        avg_com_info['down_num'] = len(down)
        avg_com_info['down_rate'] = len(down)/(len(up)+len(down))
        avg_com_info['total_num'] = len(up)+len(down)
        if len(up)+len(down) + 20 < len(index):
            raise TickerError(f"{index}: {end_date.strftime('%Y-%m-%d')} 有超过20支股票没有数据，请确保输入的日期当天有开市\n")

        return avg_com_info

    def clean_sp500(self):
        self.sp500 = []

    def clean_ndx100(self):
        self.ndx100 = []

if __name__ == "__main__":
    import stooq
    tickers = ["spy","qqq","didi"]
    admin_msg = ""
    notify_msg = ""

    for ticker in tickers:
        try:
            a = Ticker(ticker,datetime.date(2021,8,6))
            #a.load_data(source = "~/Downloads/data")
            a.load_data(source = "stooq")
            lastest_price = a.load_data(source = "~/Downloads/data")['Close'][-1]
            a.append_sma(10)
            a.append_sma(50)
            a.append_sma(100)
            a.append_sma(200)
            a.cal_sams_change_rate()
            notify_msg += f"{lastest_price} {a.smas} {a.smas_state}\n"
        except TickerError as e:
            admin_msg += str(e)
    print("=================================")
    print(a.load_data(source = "stooq"))
    print(a.load_data(source = "stooq")['Close'][-1])
    print("=================================")
    print(notify_msg)
    print(admin_msg)
