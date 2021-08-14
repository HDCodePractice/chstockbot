from logging import error
from typing import Tuple
import pandas_datareader.data as web
import pandas as pd
import datetime
from datetime import timedelta
import os
#import stooq

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
    date_list = {}
    profit_msg = {}
    xyh_msg = {}

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

    def get_date_list(self,start=None,end=None,freq='W-WED'):
        if end is None:
            end = self.end_date
        if start is None:
            start = self.start_date
        df = self.data
        date_list = pd.date_range(start=start, end=end, freq=freq).tolist()

        for index, date in enumerate(date_list):
            if date not in df.index:
                date_list[index]=date + datetime.timedelta(days=1)
        self.date_list = pd.to_datetime(date_list).sort_values()
        return self.date_list

    def get_price_lists(self,week_num =2): 
        """
        获得某段时间内的特定日子的价格数据，此处为周三
        """
        self.price_lists = {}
        if self.data is None:
            self.load_data()
        if self.date_list is None:
            self.get.date_list()

        df = self.data
        df_w = []
        df_m = []
        for date in self.date_list:
            df_w.append(df.loc[date, 'Close'])
            if get_week_num(date.year, date.month, date.day) == week_num:
                df_m.append(df.loc[date, 'Close'])
        
        self.price_lists['weekly'] = df_w
        self.price_lists['monthly'] = df_m
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
    
    def ge_profit_msg(self):
        self.profit_msg = {}
        if self.data is None:
            self.load_data()
        if self.date_list is None:
            self.get.date_list()
        if self.price_lists is None:
            self.get_price_lists()

        w_profit = self.cal_profit('weekly')
        m_profit = self.cal_profit('monthly')
        
        self.profit_msg['weekly'] = f"如果从{self.start_date}开始，每周三定投{self.symbol.upper()} 100元，截止到{self.end_date}，累计投入{w_profit['cost']}，市值为{w_profit['value']}，利润率为 {w_profit['rate']}"

        self.profit_msg['montly'] = f"如果从{self.start_date}开始，每月第二周的周三定投{self.symbol.upper()} 100元，截止到{self.end_date}，累计投入{m_profit['cost']}，市值为{m_profit['value']}，利润率为 {m_profit['rate']}"

        return self.profit_msg

    def clean_price_lists(self):
        self.price_lists = {}

    def append_sma(self,ma=10):
        # 数据没加载
        if self.data is None:
            self.load_data()
        
        df = self.data
        
        # if df.count()[0] < ma :
        #     raise TickerError(f"{self.symbol}里的历史数据没有{ma}这么多")

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

    def ge_xyh_msg(self, mas):
        self.xyh_msg = {}
        status_msg = ""
        if self.data is None:
            self.load_data()
        latest_price = self.data['Close'][-1]
        lowest_price = self.data['Low'][-1]
        highest_price = self.data['High'][-1]
        for ma in mas:
            if ma < self.data.count()[0]:
                self.append_sma(ma=ma)
                self.cal_sams_change_rate()
                status_msg += f"{self.smas_state[ma][1]} {ma} 周期均价：{self.smas[ma]:0.2f} ({self.smas_state[ma][0]:0.2f}%)\n"            
            else:
                status_msg += f"{self.symbol}里的历史数据没有{ma}这么多\n"
        self.xyh_msg = f"{self.symbol.upper()} 收盘价：{latest_price} ({lowest_price} - {highest_price})\n{status_msg}\n"
        return self.xyh_msg

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
    compare_msg = {}
    index_msg = {}
    
    
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

    def compare_avg(self, ma=50, source="~/Downloads/data", end_date=datetime.date.today()):
        if self.tickers is None:
            self.get_index_tickers_list()
        self.compare_msg = {}
        up = []
        down = []
        err_msg = ""
        for symbol in self.tickers:
            try:
                symbol = Ticker(symbol,end_date= end_date)
                df = symbol.load_data(source)
                lastest_price = df['Adj Close'][-1]
                symbol.append_sma(50)
                if df.count()[0] > ma :
                    if lastest_price < symbol.smas[ma]:
                        up.append(symbol.symbol)
                    else:
                        down.append(symbol.symbol)
                else:
                    err_msg +=f"{symbol.symbol.upper()} 的{ma}周期均价因时长不足无法比较\n" 
            except Exception as e:
                    err_msg += f"unreachable stock: {symbol.symbol.upper()}\nerror message: {e}\n"
                    #raise TickerError(err_msg)
                    
        
        self.compare_msg['up'] = up
        self.compare_msg['down'] = down
        self.compare_msg['err'] = err_msg
        
        return self.compare_msg

    def ge_index_compare_msg(self,index, end_date):
        if self.tickers is None:
            self.get_index_tickers_list()
        if self.compare_msg is None:
            self.compare_avg()
        self.index_msg = {}
        up_num = len(self.compare_msg['up'])
        down_num = len(self.compare_msg['down'])
        if self.compare_msg['down']:           
            self.index_msg = f"{self.symbol.upper()}共有{up_num+down_num}支股票，共有{up_num/(up_num+down_num)*100:.2f}%高于50周期均线"
        else:
            raise TickerError (f"数据好像出问题了，请检查一下。")
        if up_num+down_num + 20 < len(self.tickers):
            raise TickerError (f"{index.upper()}: {end_date.strftime('%Y-%m-%d')} 有超过20支股票没有数据，请确保输入的日期当天有开市\n")
        
        return self.index_msg


if __name__ == "__main__":
#     # Ticker测试代码
#     aapl = Ticker('AAPL')
#     aapl.load_data("~/Downloads/data")
#     aapl.get_date_list()
# #    print(aapl.get_date_list())
#     print(aapl.get_price_lists('monthly'))


    # spx = Index('ndx')
    # print(spx.get_index_tickers_list())
    # print(len(spx.tickers))
    # print(spx.compare_avg(
    #     10,
    #     source="~/Downloads/data",
    #     end_date=datetime.date(2021,6,1)
    # ))


    import stooq
    tickers = ["ndx","spx"]
    #tickers = ["aapl","RBLX"]
    admin_msg = ""
    notify_msg = ""
    mas = [10, 50, 120]
    # for ticker in tickers:
    #     try:
    #         a = Ticker(ticker,datetime.date(2021,8,10))
    #         #a.load_data(source = "~/Downloads/data")
    #         a.load_data(source = "stooq")
    #         lastest_price = a.load_data('stooq')['Close'][-1]
    #         a.append_sma(10)
    #         a.append_sma(50)
    #         a.append_sma(100)
    #         a.append_sma(200)
    #         a.cal_sams_change_rate()
    #         a.ge_xyh_msg(mas)
    #         notify_msg += f"{lastest_price} \n{a.smas} \n{a.smas_state}\n{a.xyh_msg}"
    #     except TickerError as e:
    #         admin_msg += str(e)
    # print("=================================")
    # #print(a.load_data(source = "stooq"))
    # #print(a.load_data(source = "stooq")['Close'][-1])
    # print("=================================")
    # print(notify_msg)
    # print(admin_msg)

    for ticker in tickers:
        try:
            b = Index(ticker)
            b.get_index_tickers_list()
            b.compare_avg(ma = 50, source="~/Downloads/data",end_date=datetime.date(2021,7,21))
            b.ge_index_compare_msg(ticker, end_date=datetime.date(2021,7,21))
            notify_msg += f"{b.index_msg}\n"
            admin_msg += f"{b.compare_msg['err']}\n"
        except TickerError as e:
            admin_msg += str(e)
            
        
    print (notify_msg)
    print ("(=================)")
    print (admin_msg)