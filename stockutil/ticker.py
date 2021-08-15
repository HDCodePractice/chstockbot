import pandas_datareader.data as web
import datetime
from stockutil.stooq import search_file,read_stooq_file,maNotEnoughError,markCloseError
from pandas_datareader._utils import RemoteDataError
from telegram import Bot
import getopt,sys,os
import config
from util.utils import is_second_wednesday,get_target_date

class TickerError(Exception):
    pass

class Ticker:
    df = None
    starttime = None
    endtime = None
    principle = 100
    from_s=None
    ds=None
    xmm_profit = {}
    dmm_profit = {}
    smas = {}
    smas_state ={}
    date_list= None
    def __init__(self,symbol,from_s,ds,starttime=datetime.date(2021,1,1),endtime=datetime.datetime.today(),principle=100):
        self.symbol = symbol
        self.starttime=starttime
        self.endtime = endtime
        self.from_s = from_s
        self.ds = ds
        self.principle = principle
        if starttime >= endtime:
            raise TickerError("起始时间比结束时间大，请重新设置")
        self.date_list = get_target_date(starttime,endtime)
        self.reset_data()
        
    def load_data(self):
        '''
        from_s: web/local;
        ds: "data source name" when from = "web"; "path directory" when from = "local"
        '''
        if self.ds !=None:
            if self.from_s.lower() == "web":
                df = web.DataReader(self.symbol.upper(), self.ds,start=self.starttime,end=self.endtime)
                df = df.sort_values(by="Date") #将排序这个步骤放在了判断df是否存在之后；最新的数据在最后
                if "Adj Close" not in df.columns.values: #当数据没有adj close时，从close 数据copy给adj close
                    df["Adj Close"] = df["Close"]
            if self.from_s.lower() == "local":
                tiker_file = search_file(self.symbol.lower().replace(".","-") + ".us.txt",os.path.expanduser(self.ds))
                df = read_stooq_file(path=tiker_file[0])
                #filter df based on end time
                if self.endtime in self.df.index.date:
                    df = df.loc[df.index[0]:self.endtime]
            self.df = df
            return self.df
        raise TickerError("无法使用当前指定的方法")    

    def cal_profit(self):
        dmm_stock_number = 0 #初始化 大毛毛股数
        xmm_stock_number = 0 #初始化 小毛毛股数
        second_wednesday_count = 0
        if self.df is None:
            self.load_data()
        if self.date_list == None:
            raise TickerError("指定日期中没有日期数据")
        for date in self.date_list:
            price = self.df.loc[date,"Close"] #获取周三当日的收盘价
            if is_second_wednesday(date):
                second_wednesday_count +=1 #如果当天是当月第二个周三，大毛毛个数+1
                dmm_stock_number += self.principle/price #获取大毛毛股数
            xmm_stock_number += self.principle/price #获取小毛毛股数
        self.xmm_profit = {
            "current_profit":xmm_stock_number * self.df["Close"][-1],
            "total_principle":self.principle * len(self.date_list),
            "profit_percentage": (xmm_stock_number * self.df["Close"][-1])/(self.principle * len(self.date_list)) - 1 
            } 
        if second_wednesday_count > 0:    
            self.dmm_profit = {
                "current_profit":dmm_stock_number * self.df["Close"][-1],
                "total_principle":self.principle * second_wednesday_count, 
                "profit_percentage": (dmm_stock_number * self.df["Close"][-1])/(self.principle * second_wednesday_count) - 1
                }
        return [self.xmm_profit,self.dmm_profit]

    def symbol_above_moving_average(self,ma=50):
        if self.df is None:
            self.load_data()
        if self.df.count()[0] > ma :
            if self.df['Adj Close'][-1] < self.df.tail(ma)['Adj Close'].mean():
                return False
            else:
                return True
        raise maNotEnoughError(f"{ma} 周期均价因时长不足无法得出\n")
        
    def cal_symbols_avg(self,ma:list):
        if self.df is None:
            self.load_data()
        
        df = self.df
        
        if df.count()[0] < ma :
            raise TickerError(f"Ticker{self.symbol}里的历史数据没有{ma}这么多")

        if self.endtime != df.index.date[-1]:
            raise TickerError(f"最后一个交易日不是{self.endtime}")

        sma = df.tail(ma)['Adj Close'].mean()
        self.smas[ma] = sma
        return sma

    def cal_sams_change_rate(self):
        df = self.df
        for ma,value in self.smas.items():
            percentage = (df['Adj Close'][-1] - value)/value * 100
            self.smas_state[ma] = [percentage,"🟢" if percentage > 0 else "🔴"]
        return self.smas_state

    def reset_data(self):
        self.smas = {}
        self.smas_state = {}

    def gen_mmt_msg(self):
        chat_msg = ""
        if self.xmm_profit:
            chat_msg += f"如果你从{self.starttime.strftime('%Y年%m月%d日')}定投 #小毛毛 {self.symbol} {self.principle}元，到{self.endtime.strftime('%Y年%m月%d日')}累计投入 {self.xmm_profit['total_principle']}元，到昨日市值为 {self.xmm_profit['current_profit']:0.2f} 元，累计利润为 {self.xmm_profit['profit_percentage']*100:0.2f}%\n"
        if self.dmm_profit:
            chat_msg += f"如果你从{self.starttime.strftime('%Y年%m月%d日')}定投 #大毛毛 {self.symbol} {self.principle}元，到{self.endtime.strftime('%Y年%m月%d日')}累计投入 {self.dmm_profit['total_principle']}元，到昨日市值为 {self.dmm_profit['current_profit']:0.2f} 元，累计利润为 {self.dmm_profit['profit_percentage']*100:0.2f}%\n"
        return chat_msg

    def gen_xyh_msg(self):
        chat_msg = f"{self.symbol}价格: {self.df['Close'][-1]}({self.df['Low'][-1]} - {self.df['High'][-1]}):\n"
        for key,value in self.smas.items():
            chat_msg += f"{self.smas_state[key][1]} {key} 周期均价：{value:0.2f} ({self.smas_state[key][0]:0.2f}%)\n"
        return chat_msg
