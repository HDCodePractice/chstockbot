import pandas as pd
import datetime
import pandas_datareader.data as web
from stockutil import stooq,wikipedia
from stockutil.stooq import search_file,read_stooq_file,maNotEnoughError,markCloseError
from pandas_datareader._utils import RemoteDataError
from telegram import Bot
import getopt,sys,os
import config

class Ticker:
    df = pd.DataFrame()
    notify_msg = ""
    admin_msg = ""
    starttime = datetime.datetime.today()
    endtime = datetime.datetime.today()
    source = "stooq"
    principle = 100
    path =f"{config.config_path}/data"
    profit = []
    def __init__(self,symbol):
        self.symbol = symbol
        
    def load_web_data(self):
        try:
            self.df = web.DataReader(self.symbol.upper(), self.source,start=self.starttime,end=self.endtime)
            self.df = self.df.sort_values(by="Date") #将排序这个步骤放在了判断df是否存在之后；最新的数据在最后
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

    def generate_mmt_msg(self,xmm_profit:dict,dmm_profit:dict): #生成定投信息
        xmm_msg = f"如果你从{self.starttime.strftime('%Y年%m月%d日')}定投 #小毛毛 {self.symbol} {self.principle}元，到{self.endtime.strftime('%Y年%m月%d日')}累计投入 {xmm_profit['total_principle']}元，到昨日市值为 {xmm_profit['current_profit']:0.2f} 元，累计利润为 {xmm_profit['profit_percentage']*100:0.2f}%\n"
        dmm_msg = f"如果你从{self.starttime.strftime('%Y年%m月%d日')}定投 #大毛毛 {self.symbol} {self.principle}元，到{self.endtime.strftime('%Y年%m月%d日')}累计投入 {dmm_profit['total_principle']}元，到昨日市值为 {dmm_profit['current_profit']:0.2f} 元，累计利润为 {dmm_profit['profit_percentage']*100:0.2f}%\n"

        if is_second_wednesday(d=self.endtime):
            self.notify_msg += dmm_msg
        self.notify_msg += xmm_msg
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

if __name__ == "__main__":
    #debug code
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:s:e:", ["config=","starttime=","endtime="])
    except getopt.GetoptError:
        print(help())
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(help())
            sys.exit()
        elif opt in ("-c", "--config"):
            config.config_path = arg  
        elif opt in ("-s", "--starttime"): #setup datetime format "yyyymmdd"
            try: #尝试对从参数中读取的日期进行日期格式转换，如果没有参数，则使用1/26/2021
                target_start_time = datetime.datetime.strptime(arg,"%Y%m%d").date()
            except:
                print(f"无法读取日期：\n{help()}")
                sys.exit(2)
        elif opt in ("-e", "--endtime"):
            try: #尝试对从参数中读取的日期进行日期格式转换，如果没有参数，则使用1/26/2021
                target_end_time = datetime.datetime.strptime(arg,"%Y%m%d").date()
            except:
                print(f"无法读取日期：\n{help()}")
                sys.exit(2)

        

    config.config_file = os.path.join(config.config_path, "config.json")
    try:
        CONFIG = config.load_config()
    except FileNotFoundError:
        print(f"config.json not found.Generate a new configuration file in {config.config_file}")
        config.set_default()
        sys.exit(2)

    bot = Bot(token = CONFIG['Token'])
    symbols = CONFIG['mmtticker']
    adminchat = CONFIG['xyhlog']
    debug = CONFIG['DEBUG']
    ds = CONFIG['xyhsource']   
    mmtchat = CONFIG['mmtchat'] 
    admin_message = ""
    ticker = Ticker("qqq")
    ticker.load_web_data()
    ticker.cal_profit()
    ticker.generate_mmt_msg(ticker.profit[0],ticker.profit[1])
    if ticker.admin_msg:
        sendmsg(bot,mmtchat,ticker.admin_msg,debug=debug)
    if ticker.notify_msg:
        sendmsg(bot,mmtchat,ticker.notify_msg,debug=debug)

