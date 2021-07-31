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
    path =f"{config.config_path}/data"
    dmm_stock_number = 0 #初始化 大毛毛股数
    xmm_stock_number = 0 #初始化 小毛毛股数
    second_wednesday_count = 0
    principle = 100
    profit = []
    def __init__(self,symbol):
        self.symbol = symbol
        
    def load_data(self,type="internet",source = source,start = starttime,end = endtime):
        '''
        type: internet/local
        source: data source/local path
        '''
        self.starttime = start
        self.endtime = end
        self.source = source
        if type == "internet":
            try:
                self.df = web.DataReader(self.symbol.upper(), source,start=start,end=end)
                self.df = self.df.sort_values(by="Date") #将排序这个步骤放在了判断df是否存在之后；最新的数据在最后
                return True
            except NotImplementedError:
                self.admin_msg += f"当前数据源{self.source}不可用"
            except RemoteDataError:
                self.admin_msg += f"在{self.source}找不到{self.symbol}的信息\n"
            except Exception as e: 
                self.admin_msg += f"当前{self.symbol}读取报错了，具体错误信息是{e}\n"        
        else:
            tiker_file = search_file(self.symbol.lower().replace(".","-") + ".us.txt",os.path.expanduser(source))
            self.df = read_stooq_file(path=tiker_file[0])
            #filter df based on end time
            if end in self.df.index.date:
                self.df = self.df.loc[self.df.index[0]:end]
                return True
            else:
                self.admin_msg += markCloseError(f"输入的日期没有数据，请确保输入的日期当天有开市\n")
        return False  
    
    def cal_profit(self,principle=100):
        if not self.df.empty:
            date_list = pd.date_range(start=self.starttime, end=self.endtime, freq='W-WED').strftime('%Y-%m-%d').tolist()
            for date in date_list:
                price = self.df.loc[date,"Close"] #获取周三当日的收盘价
                if is_second_wednesday(datetime.datetime.strptime(date, "%Y-%m-%d")):
                    self.second_wednesday_count +=1 #如果当天是当月第二个周三，大毛毛个数+1
                    self.dmm_stock_number += principle/price #获取大毛毛股数
                self.xmm_stock_number += principle/price #获取小毛毛股数
            xmm_profit = {
                "current_price": self.df["Close"][-1], 
                "current_profit":self.xmm_stock_number * self.df["Close"][-1],
                "total_principle":principle * len(date_list),
                "profit_percentage": (self.xmm_stock_number * self.df["Close"][-1])/(principle * len(date_list)) - 1 
                } 
            dmm_profit = {
                "current_price": self.df["Close"][-1], 
                "current_profit":self.dmm_stock_number * self.df["Close"][-1],
                "total_principle":principle * self.second_wednesday_count, 
                "profit_percentage": (self.dmm_stock_number * self.df["Close"][-1])/(principle * self.second_wednesday_count) - 1
                } 
            self.profit = [xmm_profit,dmm_profit]
            return True
        else:
            self.admin_msg += f"当前没有数据，请检查数据源是否工作\n"
            return False

    def get_spx_ndx_avg_msg(self,ma=50):
        """
        获取spx和ndx在50MA之上的股票数量的百分比信息，返回发给用户的信息。
        """
        sp500 = wikipedia.get_sp500_tickers()
        ndx100 = wikipedia.get_ndx100_tickers()
        indexes = {"SPX": sp500, "NDX": ndx100}
        # indexes = {"ndx100": ndx100}
        for key in indexes:
            up = []
            down = []       
            for symbol in indexes[key]:
                try:
                    if stooq.symbol_above_moving_average(symbol,ma=ma,path=f"{config.config_path}/data",end=self.endtime): 
                        up.append(symbol)
                    else:
                        down.append(symbol)
                except stooq.markCloseError:
                    self.admin_msg += f"{key}: {symbol} {self.endtime.strftime('%Y-%m-%d')}没有数据\n"
                    #break 移除break 防止出现只有部分ticker没有数据但是大部分有数据的情况
                except Exception as e:
                    self.admin_msg += f"unreachable stock: {symbol}\nerror message: {e}\n"
            if down:
                self.notify_msg += f"{key}共有{len(up)+len(down)}支股票，共有{len(up)/(len(up)+len(down))*100:.2f}%高于{ma}周期均线\n"
            if len(up)+len(down) + 20 < len(indexes[key]):
                self.admin_msg = f"{key}: {self.endtime.strftime('%Y-%m-%d')} 有超过20支股票没有数据，请确保输入的日期当天有开市\n"
        return True

    def generate_mmt_msg(self,xmm_profit:dict,dmm_profit:dict): #生成定投信息
        self.notify_msg = f"如果你每周定投，哪么今天是投 #小毛毛 的日子啦，今天是周三 请向小🐷🐷中塞入你虔诚的🪙吧～\n"
        xmm_msg = f"如果你从{self.starttime.strftime('%Y年%m月%d日')}定投 #小毛毛 {self.symbol} {self.principle}元，到{self.endtime.strftime('%Y年%m月%d日')}累计投入 {xmm_profit['total_principle']}元，到昨日市值为 {xmm_profit['current_profit']:0.2f} 元，累计利润为 {xmm_profit['profit_percentage']*100:0.2f}%\n"
        dmm_msg = f"如果你从{self.starttime.strftime('%Y年%m月%d日')}定投 #大毛毛 {self.symbol} {self.principle}元，到{self.endtime.strftime('%Y年%m月%d日')}累计投入 {dmm_profit['total_principle']}元，到昨日市值为 {dmm_profit['current_profit']:0.2f} 元，累计利润为 {dmm_profit['profit_percentage']*100:0.2f}%\n"

        if is_second_wednesday(d=self.endtime):
            self.notify_msg += f"如果你每月定投，哪么今天是投 #大毛毛 的日子啦，今天是本月第二周的周三 请向小🐷🐷中塞入你虔诚的💰吧～\n"
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
    ticker.load_data(type="internet",source="stooq",start=datetime.date(2021,5,5))
    ticker.cal_profit()
    ticker.generate_mmt_msg(ticker.profit[0],ticker.profit[1])
    if ticker.admin_msg:
        sendmsg(bot,mmtchat,ticker.admin_msg,debug=debug)
    if ticker.notify_msg:
        sendmsg(bot,mmtchat,ticker.notify_msg,debug=debug)

