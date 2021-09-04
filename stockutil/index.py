import datetime

from stockutil.ticker import Ticker
import pandas as pd
from stockutil.stooq import list_file_prefix
class IndexError(Exception):
    pass

class Index:
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
    #错误信息
    err_msg = ""
    
    def __init__(self,symbol,from_s="sources",local_store="data"):
        #from_s: sources or markets 数据需要计算指数还是市场 : sources/markets
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
    
    def compare_avg_ma(self, ma=10, end_date=datetime.date.today()): #分开计算ticker的信息
        self.up = []
        self.down = []
        self.ma =ma
        for ticker in self.tickers:
            # TODO: 这里为什么要把再写一遍呢？Ticker里的功能已经写好了啊？
            symbol = Ticker(ticker,"local",ds=self.local_store,endtime=end_date)
            try:
                df = symbol.load_data()
                if end_date in df.index.date:                
                    df = df.loc[df.index[0]:end_date]
                    if df.count()[0] > ma :
                        if df['Adj Close'][-1] < df.tail(ma)['Adj Close'].mean(): #将股票信息存入列表
                            self.down.append(symbol.symbol)
                        else:
                            self.up.append(symbol.symbol)
                        self.today_vol += df["Volume"][-1] #今日交易量
                        self.yesterday_vol += df["Volume"][-2] #昨日交易量
                    else:
                        raise IndexError(f"{symbol.symbol} {ma} 周期均价因时长不足无法得出")
                else:
                    raise IndexError(f"{symbol.symbol}输入的日期没有数据，请确保输入的日期当天有开市\n{symbol.df}")
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
    
    def gen_index_msg(self,end_time): #生成指数信息
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