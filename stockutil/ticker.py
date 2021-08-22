from logging import error
from typing import Tuple
from numpy import append, dtype
import os
import pandas_datareader.data as web
import pandas as pd
import datetime
from datetime import date, timedelta
from stockutil.stooq import search_file,read_stooq_file
from util.utils import get_week_num, get_dmm_maxtry,get_default_maxtry,get_xmm_maxtry, get_date_list

class TickerError(Exception):
    pass

class Ticker:
    symbol = None
    data = None
    start_date = None
    end_date = None
    # Ticker的SMA及对应的值
    smas = {}
    # Ticker的SMA所对应的状态[change_rate,flag]
    smas_state = {}
    date_lists = {}      #给定规则下的日期列表
    price_lists = {}     #日期列表对应的价格列表
    profit_msg = {}
    xyh_msg = {}

    def __init__(self, symbol, start_date, end_date=datetime.date.today()):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.date_lists = get_date_list(start_date, end_date)

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
            ticker_file = search_file(symbol.lower().replace(".","-") + ".us.txt",os.path.expanduser(source))
            df = read_stooq_file(path = ticker_file[0])
            self.data = df
            self.clean_sma()
            self.clean_price_lists()
        self.end_date = df.index.date[-1]
        if self.start_date < df.index.date[0]:
            self.start_date = df.index.date[0]
        return self.data


    def get_price_list(self, date_list_name, get_maxtry =get_default_maxtry): 
        """
        获得给定日期列表的收盘价数据
        """
        price_list = []
        if self.data is None:
            self.load_data()
        if self.date_lists is None:
            self.date_lists = get_date_list(self.start_date, self.end_date)
        if date_list_name not in self.date_lists.keys():
            raise TickerError(f"{self.symbol} 没有 {date_list_name} 的日期列表")
        df = self.data
        date_list = self.date_lists[date_list_name]
        for j in range(len(date_list)):
            if date_list[j] > df.index[0]:
                cal_date = date_list[j]
                max_try = get_maxtry(cal_date)
                i = 0 
                while cal_date not in df.index.date and i < max_try:
                    i += 1
                    cal_date = cal_date + datetime.timedelta(days=1)
                if i < max_try:
                    price_list.append(df.loc[cal_date]['Close'])        
        self.price_lists[date_list_name] = price_list
        return self.price_lists

    def cal_profit(self, date_list_name):
        """
        计算某ticker指定时间段的利润率。
        Parameters
        ----------
        ticker_price : 每个定投日的收盘价格列表。 
        """
        if date_list_name not in self.date_lists.keys():
            raise TickerError(f"{self.symbol} 没有 {date_list_name} 的周期价格列表")
        ticker_price = self.price_lists[date_list_name]
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
        if self.price_lists is None:
            self.get_price_list()

        w_profit = self.cal_profit('xmm')
        m_profit = self.cal_profit('dmm')
        
        self.profit_msg['weekly'] = f"如果从{self.start_date}开始，每周三定投{self.symbol.upper()} 100元，截止到{self.end_date}，累计投入{w_profit['cost']}，市值为{w_profit['value']}，利润率为 {w_profit['rate']}"
        self.profit_msg['monthly'] = f"如果从{self.start_date}开始，每月第二周的周三定投{self.symbol.upper()} 100元，截止到{self.end_date}，累计投入{m_profit['cost']}，市值为{m_profit['value']}，利润率为 {m_profit['rate']}"


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


if __name__ == "__main__":
#     # Ticker测试代码
    aapl = Ticker('AAPL', end_date=datetime.date.today())
    aapl.load_data("~/Downloads/data")
    aapl.get_date_list()
    aapl.get_price_lists()
    aapl.cal_profit('weekly')
    aapl.cal_profit('monthly')
    print(aapl.get_date_list())
    # print(aapl.ge_profit_msg()['weekly'])
    # print(aapl.ge_profit_msg()['montly'])


    #spx = Index('ndx')
    # print(spx.get_index_tickers_list())
    # print(len(spx.tickers))
    # print(spx.compare_avg(
    #     10,
    #     source="~/Downloads/data",
    #     end_date=datetime.date(2021,6,1)
    # ))

    

    # for ticker in tickers:
    #     try:
    #         b = Index(ticker)
    #         b.get_index_tickers_list()
    #         b.compare_avg(ma = 50, source="~/Downloads/data",end_date=datetime.date(2021,7,21))
    #         b.ge_index_compare_msg(ticker, end_date=datetime.date(2021,7,21))
    #         notify_msg += f"{b.index_msg}\n"
    #         admin_msg += f"{b.compare_msg['err']}\n"
    #     except TickerError as e:
    #         admin_msg += str(e)
            
        
    # print (spx_avg)
    # print (notify_msg)
    # print (admin_msg)
