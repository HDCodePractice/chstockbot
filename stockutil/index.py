import datetime
from stockutil.ticker import Ticker
import pandas as pd
class IndexError(Exception):
    pass

class Index:
    #指数代码
    symbol = None
    #均线周期
    ma=None
    #指数成分股列表
    tickers = []
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
    #错误信息
    err_msg = ""
    
    def __init__(self,symbol,local_store="~/Downloads/data") -> None:
        symbol = symbol.upper()
        if symbol not in self.sources.keys():
            raise IndexError(f"{symbol} 不在我们的支持列表中")
        self.symbol = symbol
        self.local_store = local_store

    def get_index_tickers_list(self):
        """
        获得指数的成分股列表
        """
        self.tickers = []
        url,table_num,colum_name = self.sources[self.symbol]
        df = pd.read_html(url)[table_num]
        self.tickers = df[colum_name].tolist()
        self.reset_index_data() 
        return self.tickers
 
    def compare_avg_ma(self, symbol, ma=10, end_date=datetime.date.today()): #分开计算ticker的信息
        self.ma =ma
        symbol = Ticker(symbol,"local",ds=self.local_store,endtime=end_date)
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
                return True
            else:
                raise IndexError(f"{symbol.symbol} {ma} 周期均价因时长不足无法得出\n")             
        else:
            raise IndexError(f"{symbol.symbol}输入的日期没有数据，请确保输入的日期当天有开市\n")
        
    def reset_index_data(self): #初始化数据
        self.up = []
        self.down=[]
        self.today_vol = 0
        self.yesterday_vol = 0
    
    def gen_index_msg(self,end_time): #生成指数信息
        if (len(self.up)+len(self.down) + 20 ) < len(self.tickers):
            raise IndexError(f"{self.symbol}: {end_time.strftime('%Y-%m-%d')} 有超过20支股票没有数据，请确保输入的日期当天有开市\n" )      
        if self.up == 0 or self.down == 0:
            raise IndexError(f"无法读取高于/低于周期均价的股票列表，请确认股票列表\n")
        if self.today_vol == 0 and self.yesterday_vol == 0:
            raise IndexError(f"无法读取今日和昨日的交易量， 请重新计算\n") 
        chat_msg = f"{self.symbol}共有{len(self.up)+len(self.down)}支股票，共有{len(self.up)/(len(self.up)+len(self.down))*100:.2f}%高于{self.ma}周期均线\n今日交易量与昨日交易量百分比：{(self.today_vol/self.yesterday_vol - 1)*100:.2f}%\n"
        return chat_msg