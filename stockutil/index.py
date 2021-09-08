import datetime, os
from stockutil.ticker import Ticker
import pandas as pd
from stockutil.stooq import list_file_prefix, read_stooq_file
from pathlib import Path, PurePath
import re

class IndexError(Exception):
    pass

class Index:
    #起始时间
    starttime = None
    #结束时间
    endtime = None
    #指数代码
    symbol = None
    #均线周期
    ma=None
    #指数成分股列表
    tickers = []
    #数据来源 
    # sources: 从sources中的在线数据源获取数据
    # markets: 从stooq离线文件里获取数据
    from_s = None
    #本地数据存储路径   
    local_store = ""
    #指数交易量
    today_vol = 0
    yesterday_vol =0
    #成分股列表：高于/低于x周期均价的股票列表
    up = []
    down = []
    # 下载指数成分股的数据源
    sources = {
        "NDX" : ["https://en.wikipedia.org/wiki/Nasdaq-100",3,"Ticker"],
        "SPX" : ["https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",0,"Symbol"]
    }
    #市场的数据源
    markets = ["nasdaq","nyse"]
    #市场的交易量
    market_volume={}
    #错误信息
    err_msg = ""
    
    def __init__(self,symbol,from_s="sources",local_store="data",starttime=datetime.date.today() - datetime.timedelta(days=364),endtime= datetime.date.today()):
        #from_s: sources or markets 数据需要计算指数还是市场 : sources/markets
        #starttime/endtime： 起始时间/结束时间 默认值：一年前的今天/今天
        self.from_s = from_s
        if from_s == "sources":
            symbol = symbol.upper()
            if symbol not in self.sources.keys():
                raise IndexError(f"{symbol} 不在我们的支持列表中")
        if from_s == "markets":
            if symbol not in self.markets:
                raise IndexError(f"{symbol} 不在我们的支持列表中")
        self.symbol = symbol
        self.local_store = local_store
        self.starttime = starttime
        self.endtime = endtime
        self.reset_index_data()

    def get_tickers_list(self):
        """
        获得指数的成分股列表
        """
        self.tickers = []
        if self.from_s == "sources":
            url,table_num,colum_name = self.sources[self.symbol]
            df = pd.read_html(url)[table_num]
            self.tickers = df[colum_name].tolist()
        if self.from_s == "markets":
            self.tickers = list_file_prefix(self.symbol, ".txt",self.local_store)
        #self.reset_index_data() 
        return self.tickers
    
    def compare_avg_ma(self, ma=10): #合并计算
        self.up = []
        self.down = []
        self.ma =ma
        end_date = self.endtime
        start_date = self.starttime
        for ticker in self.tickers:
            symbol = Ticker(ticker,"local",ds=self.local_store,starttime=start_date,endtime=end_date)
            try:
                df = symbol.load_data()
                if end_date in df.index.date:                
                    df = df.loc[df.index[0]:end_date]
                    symbol.cal_symbols_avg(ma)
                    symbol.cal_sams_change_rate
                    for key,value in symbol.smas_state.items(): #从ticke的smas_state读取数据
                        if value[0] > 0:
                            self.up.append(symbol.symbol)
                        else:
                            self.down.append(symbol.symbol)
                    self.today_vol += df["Volume"][-1] #今日交易量
                    self.yesterday_vol += df["Volume"][-2] #昨日交易量
            except Exception as e:
                self.err_msg += f"{self.symbol} {e}\n"
                import traceback
                traceback.print_exc()
                continue
        return True
        
    def reset_index_data(self): #初始化数据
        self.up = []
        self.down=[]
        self.today_vol = 0
        self.yesterday_vol = 0
    
    def gen_index_msg(self): #生成指数信息
        end_time = self.endtime
        # TODO: 这个end_time参数如果和compare_avg_ma的不一样，是不是会出很神奇的结果？
        max_num = 20 if self.from_s == "sources" else 150
        if (len(self.up)+len(self.down) + max_num ) < len(self.tickers):
            raise IndexError(f"{self.symbol}: {end_time.strftime('%Y-%m-%d')} 有超过20支股票没有数据，请确保输入的日期当天有开市\n" )      
        if self.up == 0 or self.down == 0:
            raise IndexError(f"{self.symbol}无法读取高于/低于周期均价的股票列表，请确认股票列表\n")
        if self.today_vol == 0 and self.yesterday_vol == 0:
            raise IndexError(f"{self.symbol}无法读取今日和昨日的交易量， 请重新计算\n") 
        chat_msg = f"{self.symbol}共有{len(self.up)+len(self.down)}支股票，共有{len(self.up)/(len(self.up)+len(self.down))*100:.2f}%高于{self.ma}周期均线\n当日交易量变化：{(self.today_vol/self.yesterday_vol - 1)*100:.2f}%\n"
        return chat_msg

    def get_path_list(self):
        self.path_list = []
        self.err_msg=""
        text = re.compile(r".*[0-9]$") 
        for root, dirs, files in os.walk(self.local_store, topdown=False):
            try:
                for name in dirs:
                    if self.symbol in os.path.join(root, name):
                        if not text.match(os.path.join(root, name)):
                            if "nysemkt" not in os.path.join(root, name):
                                self.path_list.append(os.path.join(root, name))
            except Exception as e:
                self.err_msg += f"{type(e)},{e}\n"
        print (self.path_list)
        return self.path_list

    def compare_market_volume(self):
        self.today_vol = 0
        self.yesterday_vol = 0
        self.market_volume = {}
        for path in self.path_list:
            p = Path(path)
            self.err_msg = ""
            for file_name in p.rglob('*.txt'):
                try:
                    t = Path(file_name)
                    ticker_file = read_stooq_file(file_name)  
                    ticker_name = t.stem
                    if self.endtime in ticker_file.index.date:                
                        ticker_file = ticker_file.loc[ticker_file.index[0]:self.endtime]
                        self.today_vol += ticker_file['Volume'][-1]
                        self.yesterday_vol += ticker_file['Volume'][-2]
                    else:
                        raise IndexError(f"{ticker_name.upper()}最新的数据不是{self.endtime}。请检查数据源。")
                except Exception as e:
                    self.err_msg += f"{type(e)},{e}\n"
                    continue
        self.market_volume[self.symbol]=[self.today_vol,self.yesterday_vol]
        print (self.market_volume)
        self.market_volume_msg = f"{self.symbol.upper()} 市场 {self.endtime} 交易量的变化为 {(self.today_vol/self.yesterday_vol-1)*100:.2f}%\n"
        return self.market_volume_msg
    
