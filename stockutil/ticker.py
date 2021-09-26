import pandas_datareader.data as web
import pandas as pd
import datetime
from stockutil.stooq import search_file,read_stooq_file,maNotEnoughError,markCloseError
import os
from util.utils import is_second_wednesday,get_target_date,get_dmm_maxtry,get_xmm_maxtry
from pandas.errors import EmptyDataError

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
    date_list= {}
    price_list={}
    xmm_price_list = {}
    dmm_price_list = {}

    def __init__(self,symbol,from_s,ds,starttime=datetime.date.today() - datetime.timedelta(days=365),endtime=datetime.date.today(),principle=100):
        if isinstance(starttime,datetime.datetime):
            starttime = starttime.date()
        if isinstance(endtime,datetime.datetime):
            endtime = endtime.date()
        self.symbol = symbol.upper()
        self.starttime=starttime
        self.endtime = endtime
        self.from_s = from_s
        self.ds = ds
        self.principle = principle
        if starttime >= endtime:
            raise TickerError("起始时间比结束时间大，请重新设置")
        self.date_list = get_target_date(starttime,endtime)
        
        
    def load_data(self, updateEndtime=False):
        '''
        from_s: web/local;
        ds: "data source name" when from = "web"; "path directory" when from = "local"
        '''
        if self.ds !=None:
            if self.from_s.lower() == "web":
                df = web.DataReader(self.symbol.upper(), self.ds,start=self.starttime,end=self.endtime)
                if len(df.index) < 1:
                    raise TickerError("请检查输入的股票名称，{self.symbol.upper()}好像不存在。")    
                df = df.sort_values(by="Date") #将排序这个步骤放在了判断df是否存在之后；最新的数据在最后
                if "Adj Close" not in df.columns.values: #当数据没有adj close时，从close 数据copy给adj close
                    df["Adj Close"] = df["Close"]
            if self.from_s.lower() == "local":
                tiker_file = search_file(self.symbol.lower().replace(".","-") + ".us.txt",os.path.expanduser(self.ds))
                try:
                    df = read_stooq_file(path=tiker_file[0])
                except EmptyDataError:
                    raise TickerError(f"{self.symbol}:{self.endtime}无数据")
                #filter df based on end time
            #判断是否需要更新endtime
            #无论从本地还是stooq，似乎都需要对start，end的时间做一下处理
            if self.endtime in df.index.date:
                df = df.loc[df.index[0]:self.endtime]
            else:
                if updateEndtime == False:
                    raise TickerError(f"{self.symbol}:{self.endtime}无数据")
                self.endtime = df.index[-1].date()
            #根据df的值更新starttime的日期 防止出现startime没有数据
            if self.starttime not in df.index.date:
                self.starttime = df.index.date[0]
            self.df = df
            self.reset_data()
            
            return self.df
        raise TickerError("无法使用当前指定的方法")    


    def get_target_price(self,mmt,date,max_try):
        #mmt = dmm or xmm
        if self.df is None:
            self.load_data()
        #start from first day of the data
        i = 0
        while i <  max_try:
            tmp_date = date + datetime.timedelta(days=i)
            if tmp_date.date() in self.df.index.date:
                if mmt == "xmm":
                    self.xmm_price_list[tmp_date] = self.df.loc[tmp_date,"Close"]
                if mmt == "dmm":
                    self.dmm_price_list[tmp_date] = self.df.loc[tmp_date,"Close"]
                break
            i +=1
        return True
        
    def get_price_list(self):
        if self.df is None:
            self.load_data()
        if self.date_list == None:
            raise TickerError("指定日期中没有日期数据")
        for date in self.date_list['xmm']:
            self.get_target_price("xmm",date,get_xmm_maxtry(date))
        for date in self.date_list['dmm']:
            self.get_target_price("dmm",date,get_dmm_maxtry(date))
        return True


    
    def cal_profit(self):
        dmm_stock_number = 0 #初始化 大毛毛股数
        xmm_stock_number = 0 #初始化 小毛毛股数
        if self.get_price_list():
            for date,price in self.xmm_price_list.items():
                xmm_stock_number += self.principle/price #获取小毛毛股数
            for date,price in self.dmm_price_list.items():
                dmm_stock_number += self.principle/price #获取大毛毛股数
            self.xmm_profit = {
                "current_price":xmm_stock_number * self.df["Close"][-1],   #当前市值
                "total_principle":self.principle * len(self.xmm_price_list),  # 总成本
                "profit_percentage": (xmm_stock_number * self.df["Close"][-1] - self.principle * len(self.xmm_price_list))/(self.principle * len(self.xmm_price_list)) #盈利百分比
                } 
            if len(self.dmm_price_list) > 0:    
                self.dmm_profit = {
                    "current_price":dmm_stock_number * self.df["Close"][-1],#当前市值
                    "total_principle":self.principle * len(self.dmm_price_list), # 总成本
                    "profit_percentage": (dmm_stock_number * self.df["Close"][-1] - self.principle * len(self.dmm_price_list))/(self.principle * len(self.dmm_price_list)) #盈利百分比
                    }
            return True
        raise TickerError("无法获得价格列表")


    def symbol_above_moving_average(self,ma=50):
        """
        获取一个Ticker在self.endtime是否高于指定的历史平均价。返回True高于avg，Flase低于avg

        Parameters
        ----------
        ma : int, default 50
            计算的历史时长，默认为50MA
        """
        if self.df is None:
            self.load_data()
        if self.df.count()[0] > ma :
            if self.df['Adj Close'][-1] < self.df.tail(ma)['Adj Close'].mean():
                return False
            else:
                return True
        raise maNotEnoughError(f"{self.symbol} {ma} 周期均价因时长不足无法得出\n")
        
    def cal_symbols_avg(self,ma:int):
        if self.df is None:
            self.load_data()
        
        df = self.df
        
        if df.count()[0] < ma :
            raise TickerError(f"{self.symbol}里的历史数据没有{ma}这么多")

        if self.endtime != df.index.date[-1]:
            raise TickerError(f"{self.symbol}最后一个交易日不是{self.endtime}")

        sma = df.tail(ma)['Adj Close'].mean()
        self.smas[ma] = sma
        self.cal_sams_change_rate()
        return sma

    def cal_sams_change_rate(self):
        df = self.df
        for ma,value in self.smas.items():
            percentage = (df['Adj Close'][-1] - value)/value * 100
            self.smas_state[ma] = [percentage,"🟢" if percentage > 0 else "🔴"]
        return self.smas_state
    
    def cal_today_price_rate(self): #计算今日与昨日的收盘价差异
        df = self.df
        percentage = (df['Adj Close'][-1] - df['Adj Close'][-2])/df['Adj Close'][-2] * 100
        return percentage, "🟢" if percentage > 0 else "🔴"

    def get_today_price_msg(self):
        if self.df is None:
            self.load_data()
        if self.endtime > self.df.index.date[-1]:
            raise TickerError(f"{self.symbol} {self.endtime} 没有数据")
        percent,flag = self.cal_today_price_rate()
        return f"{self.symbol}价格: {flag} {self.df['Close'][-1]:.2f} {percent:.2f}% ({self.df['Low'][-1]:.2f} - {self.df['High'][-1]:.2f}):\n"

    def reset_data(self):
        self.smas = {}
        self.smas_state = {}

    def gen_mmt_msg(self):
        chat_msg = ""
        if self.xmm_profit:
            chat_msg += f"从{self.starttime.strftime('%Y年%m月%d日')}定投 #小毛毛 {self.symbol}，到{self.endtime.strftime('%Y年%m月%d日')}累计投入 {self.xmm_profit['total_principle']}元，到昨日市值为 {self.xmm_profit['current_price']:0.2f} 元，利润为 {self.xmm_profit['profit_percentage']*100:0.2f}%\n"
        if self.dmm_profit:
            chat_msg += f"从{self.starttime.strftime('%Y年%m月%d日')}定投 #大毛毛 {self.symbol}，到{self.endtime.strftime('%Y年%m月%d日')}累计投入 {self.dmm_profit['total_principle']}元，到昨日市值为 {self.dmm_profit['current_price']:0.2f} 元，利润为 {self.dmm_profit['profit_percentage']*100:0.2f}%\n"
        return chat_msg

    def gen_xyh_msg(self):
        # 如果smas是空的怎么办？
        chat_msg = ""
        for key,value in self.smas.items():
            chat_msg += f"{self.smas_state[key][1]} {key} 周期均价：{value:0.2f} ({self.smas_state[key][0]:0.2f}%)\n"
        return chat_msg
