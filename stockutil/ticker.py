import pandas_datareader.data as web
import datetime
from stockutil.stooq import search_file,read_stooq_file,maNotEnoughError,markCloseError
import os
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
    date_list= {}
    xmm_price_list = {}
    dmm_price_list = {}

    def __init__(self,symbol,from_s,ds,starttime=datetime.date.today() - datetime.timedelta(days=365),endtime=datetime.date.today(),principle=100):
        self.symbol = symbol
        self.starttime=starttime
        self.endtime = endtime
        self.from_s = from_s
        self.ds = ds
        self.principle = principle
        if starttime >= endtime:
            raise TickerError("起始时间比结束时间大，请重新设置")
        self.date_list = get_target_date(starttime,endtime)
        
        
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
                if self.endtime in df.index.date:
                    df = df.loc[df.index[0]:self.endtime]
            self.df = df
            self.reset_data()
            return self.df
        raise TickerError("无法使用当前指定的方法")    

    def xmm_max_try(self):
        if self.date_list["xmm"] == None:
            raise TickerError("小毛毛指定日期中没有日期数据")
        return 7
    
    def dmm_max_try(self): #没有想好是要分开来算max try 还是直接给定值
        if self.date_list["dmm"] == None:
            raise TickerError("小毛毛指定日期中没有日期数据")
        return 28


    def get_target_price(self,date_list,max_try):
        if self.df is None:
            self.load_data()
        if date_list == None:
            raise TickerError("指定日期中没有日期数据")
        price_list={}
        #start from first day of the data
        for j in range(len(date_list)):
            if date_list[j] > self.df.index[0]:
                i = 0
                while i <  max_try:
                    tmp_date = date_list[j] + datetime.timedelta(days=i)
                    if tmp_date in self.df.index.date:
                        price_list[tmp_date] = self.df.loc[tmp_date,"Close"]
                        break
                    i +=1
        return price_list
        
    def cal_profit(self):
        dmm_stock_number = 0 #初始化 大毛毛股数
        xmm_stock_number = 0 #初始化 小毛毛股数
        if self.df is None:
            self.load_data()
        if self.date_list == None:
            raise TickerError("指定日期中没有日期数据")

        self.dmm_price_list = self.get_target_price(self.date_list['dmm'],self.dmm_max_try())
        self.xmm_price_list = self.get_target_price(self.date_list['xmm'],self.xmm_max_try())
        for date,price in self.xmm_price_list.items():
            xmm_stock_number += self.principle/price #获取小毛毛股数
        for date,price in self.dmm_price_list.items():
            dmm_stock_number += self.principle/price #获取大毛毛股数
        self.xmm_profit = {
            "current_profit":xmm_stock_number * self.df["Close"][-1],   #当前市值
            "total_principle":self.principle * len(self.xmm_price_list),  # 总成本
            "profit_percentage": (xmm_stock_number * self.df["Close"][-1])/(self.principle * len(self.xmm_price_list)) - 1  #盈利百分比
            } 
        if len(self.dmm_price_list) > 0:    
            self.dmm_profit = {
                "current_profit":dmm_stock_number * self.df["Close"][-1],
                "total_principle":self.principle * len(self.dmm_price_list), 
                "profit_percentage": (dmm_stock_number * self.df["Close"][-1])/(self.principle * len(self.dmm_price_list)) - 1
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
        chat_msg = ""
        for key,value in self.smas.items():
            chat_msg += f"{self.smas_state[key][1]} {key} 周期均价：{value:0.2f} ({self.smas_state[key][0]:0.2f}%)\n"
        return chat_msg



if __name__ == "__main__":
    # Ticker测试代码
    # aapl = Ticker('AAPL')
    # aapl.load_data("~/Downloads/data")
    # aapl.get_price_lists(start=datetime.date(2020,4,28))
    # print(aapl.cal_profit('montly'))


    # spx = Index('ndx')
    # print(spx.get_index_tickers_list())
    # print(len(spx.tickers))
    # print(spx.compare_avg(
    #     10,
    #     source="~/Downloads/data",
    #     end_date=datetime.date(2021,6,1)
    # ))
    ticker = Ticker("spy","web","stooq")
    print(ticker.date_list["dmm"])
    print(ticker.date_list["xmm"])
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