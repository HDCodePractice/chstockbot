from numpy import ndindex
import pandas_datareader.data as web
import pandas as pd
import datetime
import os
import stooq

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
    start_date = None
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
            self.clean_sma()
            self.clean_price_lists()
        self.end_date = df.index.date[-1]
        self.start_date = df.index.date[0]
        return self.data

    def get_price_lists(self,start=None,end=None,freq='W-WED',week_num =2): 
        """
        获得某段时间内的特定日子的价格数据，此处为周三
        """
        self.price_lists = {}
        if self.data is None:
            self.load_data()

        if end is None:
            end = self.end_date

        if start is None:
            start = self.start_date

        df = self.data
        date_list = pd.date_range(start=start, end=end, freq='W-WED').tolist()
    #    print (date_list)
        df_w = []
        df_m = []
        for date in date_list:
            df_w.append(df.loc[date, 'Close'])
            if get_week_num(date.year, date.month, date.day) == week_num:
                df_m.append(df.loc[date, 'Close'])

        self.price_lists['weekly'] = df_w
        self.price_lists['montly'] = df_m
        return self.price_lists   

    def cal_profit(self, price_list_name):
        """
        计算某ticker指定时间段的利润率。
        Parameters
        ----------
        ticker_price : 每个定投日的收盘价格列表。 
        """
        if price_list_name not in self.price_lists.keys():
            raise TickerError(f"{self.symbol} 没有 {price_list_name} 的周期价格列表")

        ticker_price = self.price_lists[price_list_name]
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
    tickers = []
    sources = {
        "NDX" : ["https://en.wikipedia.org/wiki/Nasdaq-100",3,"Ticker"],
        "SPX" : ["https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",0,"Symbol"]
    }
    
    def __init__(self,symbol) -> None:
        symbol = symbol.upper()
        if symbol not in self.sources.keys():
            raise TickerError(f"{symbol} 不在我们的支持列表中")
        self.symbol = symbol

    def get_index_tickers_list(self):
        """
        获得指数的成分股列表
        """
        self.tickers = []
        url,table_num,colum_name = self.sources[self.symbol]
        df = pd.read_html(url)[table_num]
        self.tickers = df[colum_name].tolist()
        return self.tickers

    def compare_avg(self, ma=10, source="~/Downloads/data", end_date=datetime.date.today()):
        up = []
        down = []
        for symbol in self.tickers:
            try:
                symbol = Ticker(symbol,end_date= end_date)
                df = symbol.load_data(source)
                if end_date in df.index.date:                
                    df = df.loc[df.index[0]:end_date]
                    if df.count()[0] > ma :
                        if df['Adj Close'][-1] < df.tail(ma)['Adj Close'].mean():
                            up.append(symbol.symbol)
                        else:
                            down.append(symbol.symbol)
                    else:
                        raise TickerError(f"{ma} 周期均价因时长不足无法得出\n")     
                else:
                    raise TickerError(f"输入的日期没有数据，请确保输入的日期当天有开市\n")
            except Exception as e:
                print(f"unreachable stock: {symbol.symbol}\nerror message: {e}\n")
        
        return {'up_num':len(up), 'down_num':len(down),'rate':len(up)/(len(up)+len(down))}


if __name__ == "__main__":
    # Ticker测试代码
    # aapl = Ticker('AAPL')
    # aapl.load_data("~/Downloads/data")
    # aapl.get_price_lists(start=datetime.date(2020,4,28))
    # print(aapl.cal_profit('montly'))


    spx = Index('ndx')
    print(spx.get_index_tickers_list())
    print(len(spx.tickers))
    print(spx.compare_avg(
        10,
        source="~/Downloads/data",
        end_date=datetime.date(2021,6,1)
    ))


    # import stooq
    # tickers = ["spy","qqq","didi"]
    # admin_msg = ""
    # notify_msg = ""

    # for ticker in tickers:
    #     try:
    #         a = Ticker(ticker,datetime.date(2021,8,6))
    #         #a.load_data(source = "~/Downloads/data")
    #         a.load_data(source = "stooq")
    #         lastest_price = a.load_data(source = "~/Downloads/data")['Close'][-1]
    #         a.append_sma(10)
    #         a.append_sma(50)
    #         a.append_sma(100)
    #         a.append_sma(200)
    #         a.cal_sams_change_rate()
    #         notify_msg += f"{lastest_price} {a.smas} {a.smas_state}\n"
    #     except TickerError as e:
    #         admin_msg += str(e)
    # print("=================================")
    # print(a.load_data(source = "stooq"))
    # print(a.load_data(source = "stooq")['Close'][-1])
    # print("=================================")
    # print(notify_msg)
    # print(admin_msg)
    # try:
    #     b = Index()
    #     spx = b.get_sp500_tickers()
    #     spx_avg = b.compare_avg(ma = 50, index = spx, end_date=datetime.date(2021,7,21))
    #     spx_msg = f"SPX共有{spx_avg['up_num']+spx_avg['down_num']}支股票，共有{spx_avg['rate']*100:.2f}%高于50周期均线"
    #     notify_msg = f"{spx_msg}"
    # except TickerError as e:
    #     admin_msg+=str(e)
        
    # print (spx_avg)
    # print (notify_msg)
    # print (admin_msg)