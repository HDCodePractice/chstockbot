import pandas as pd
import datetime
import pandas_datareader.data as web
from stockutil.stooq import search_file,read_stooq_file,maNotEnoughError,markCloseError
from pandas_datareader._utils import RemoteDataError
from telegram import Bot
import getopt,sys,os
import config

class Ticker:
    df = pd.DataFrame()
    xyh_msg = ""
    admin_msg = ""
    mmt_msg = ""
    starttime = datetime.date(2020,1,1)
    endtime = datetime.datetime.today()
    source = "stooq"
    principle = 100
    path =f"{config.config_path}/data"
    profit = []
    xyh_price = {}
    def __init__(self,symbol):
        self.symbol = symbol
        
    def load_web_data(self):
        try:
            self.df = web.DataReader(self.symbol.upper(), self.source,start=self.starttime,end=self.endtime)
            self.df = self.df.sort_values(by="Date") #将排序这个步骤放在了判断df是否存在之后；最新的数据在最后
            if "Adj Close" not in self.df.columns.values: #当数据没有adj close时，从close 数据copy给adj close
                self.df["Adj Close"] = self.df["Close"]
            return True
        except NotImplementedError:
            self.admin_msg += f"当前数据源{self.source}不可用"
        except RemoteDataError:
            self.admin_msg += f"在{self.source}找不到{self.symbol}的信息\n"
        except Exception as e: 
            self.admin_msg += f"当前{self.symbol}读取报错了，具体错误信息是{e}\n"        
        return False  

    def load_local_data(self):
        try:
            tiker_file = search_file(self.symbol.lower().replace(".","-") + ".us.txt",os.path.expanduser(self.path))
            self.df = read_stooq_file(path=tiker_file[0])
            #filter df based on end time
            if self.endtime in self.df.index.date:
                self.df = self.df.loc[self.df.index[0]:self.endtime]
                return True
            else:
                self.admin_msg += markCloseError(f"输入的日期没有数据，请确保输入的日期当天有开市\n")
        except Exception as e:
            self.admin_msg += f"出问题了，具体情况是{e}"
        return False

    def cal_profit(self):
        self.dmm_stock_number = 0 #初始化 大毛毛股数
        self.xmm_stock_number = 0 #初始化 小毛毛股数
        self.second_wednesday_count = 0
        if not self.df.empty:
            date_list = pd.date_range(start=self.starttime, end=self.endtime, freq='W-WED').strftime('%Y-%m-%d').tolist()
            for date in date_list:
                price = self.df.loc[date,"Close"] #获取周三当日的收盘价
                if is_second_wednesday(datetime.datetime.strptime(date, "%Y-%m-%d")):
                    self.second_wednesday_count +=1 #如果当天是当月第二个周三，大毛毛个数+1
                    self.dmm_stock_number += self.principle/price #获取大毛毛股数
                self.xmm_stock_number += self.principle/price #获取小毛毛股数
            xmm_profit = {
                "current_price": self.df["Close"][-1], 
                "current_profit":self.xmm_stock_number * self.df["Close"][-1],
                "total_principle":self.principle * len(date_list),
                "profit_percentage": (self.xmm_stock_number * self.df["Close"][-1])/(self.principle * len(date_list)) - 1 
                } 
            dmm_profit = {
                "current_price": self.df["Close"][-1], 
                "current_profit":self.dmm_stock_number * self.df["Close"][-1],
                "total_principle":self.principle * self.second_wednesday_count, 
                "profit_percentage": (self.dmm_stock_number * self.df["Close"][-1])/(self.principle * self.second_wednesday_count) - 1
                } 
            self.profit = [xmm_profit,dmm_profit]
            return True
        else:
            self.admin_msg += f"当前没有数据，请检查数据源是否工作\n"
        return False

    def symbol_above_moving_average(self,ma=50)->bool:
        if not self.df.empty:
            if self.df.count()[0] > ma :
                if self.df['Adj Close'][-1] < self.df.tail(ma)['Adj Close'].mean():
                    return False
                else:
                    return True
            else:
                self.admin_msg += maNotEnoughError(f"{ma} 周期均价因时长不足无法得出\n")
        else:
            self.admin_msg += f"当前没有数据，请检查数据源是否工作\n"
        return False
        
    def cal_symbols_avg(self,avgs:list):
        if not self.df.empty:
            try:
                if self.endtime == self.df.index.date[-1]: #做了一个checkpoint来查找今天的数据; credit for Stephen
                    self.xyh_msg += f"{self.symbol.upper()}价格: {self.df['Adj Close'][-1]:0.2f}({self.df['Low'][-1]:0.2f} - {self.df['High'][-1]:0.2f})\n"
                    for avg in avgs:
                        if self.df.count()[0] > avg :
                            #加入红绿灯的判断
                            if self.df['Adj Close'][-1] < self.df.tail(avg)['Adj Close'].mean():
                                flag = "🔴"
                            else:
                                flag = "🟢"
                            percentage = (self.df['Adj Close'][-1] - self.df.tail(avg)['Adj Close'].mean())/self.df.tail(avg)['Adj Close'].mean() * 100
                            self.xyh_msg += f"{flag} {avg} 周期均价：{self.df.tail(avg)['Adj Close'].mean():0.2f} ({percentage:0.2f}%)\n"                          
                        else:
                            self.admin_msg += f"{avg} 周期均价因时长不足无法得出\n" 
                    return True 
                else: #当天不是交易日时 返回false
                    self.admin_msg += f"今天不是交易日，不需要发送{self.symbol}信息\n"
                #当数据源成功读取并处理数据后，从当前程序break并返回信息； 防止程序运行所有的数据源
            except Exception as e: 
                self.admin_msg += f"当前{self.symbol}读取报错了，具体错误信息是{e}\n"
        else:
            self.admin_msg += f"当前没有数据，请检查数据源是否工作\n"                
        return False

    def generate_mmt_msg(self,xmm_profit:dict,dmm_profit:dict): #生成定投信息
        xmm_msg = f"如果你从{self.starttime.strftime('%Y年%m月%d日')}定投 #小毛毛 {self.symbol} {self.principle}元，到{self.endtime.strftime('%Y年%m月%d日')}累计投入 {xmm_profit['total_principle']}元，到昨日市值为 {xmm_profit['current_profit']:0.2f} 元，累计利润为 {xmm_profit['profit_percentage']*100:0.2f}%\n"
        dmm_msg = f"如果你从{self.starttime.strftime('%Y年%m月%d日')}定投 #大毛毛 {self.symbol} {self.principle}元，到{self.endtime.strftime('%Y年%m月%d日')}累计投入 {dmm_profit['total_principle']}元，到昨日市值为 {dmm_profit['current_profit']:0.2f} 元，累计利润为 {dmm_profit['profit_percentage']*100:0.2f}%\n"

        if is_second_wednesday(d=self.endtime):
            self.mmt_msg += dmm_msg
        self.mmt_msg += xmm_msg
        return True


def get_wednesday_date(start=datetime.date.today(),end=datetime.date.today()): #c获得指定日期中的周三 可以扩展成任何天数
    date_list = pd.date_range(start=start, end=end, freq='W-WED').strftime('%Y-%m-%d').tolist()
    return date_list

def is_second_wednesday(d=datetime.date.today()): #计算是否是第二个周三；网上找的，很简单又很有效
    return d.weekday() == 2 and 8 <= d.day <= 15

def sendmsg(bot,chatid,msg,debug=True):
    if debug:
        print(f"{chatid}\n{msg}")
    else:
        bot.send_message(chatid,msg)
