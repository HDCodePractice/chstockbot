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
    # 下载指数成分股的数据源
    sources = {
        "NDX" : ["https://en.wikipedia.org/wiki/Nasdaq-100",3,"Ticker"],
        "SPX" : ["https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",0,"Symbol"]
    }
    
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
        return self.tickers

    def compare_avg(self, ma=10, end_date=datetime.date.today()):
        if len(self.tickers) == 0:
            self.get_index_tickers_list()
        up = []
        down = []
        today_volume = 0
        yesterday_volume = 0
        self.ma =ma
        err_msg =""
        for symbol in self.tickers:
            try:
                symbol = Ticker(symbol,"local",ds=self.local_store,endtime=end_date)
                df = symbol.load_data()
                if end_date in df.index.date:                
                    df = df.loc[df.index[0]:end_date]
                    today_volume += df["Volume"][-1] #今日交易量
                    yesterday_volume += df["Volume"][-2] #昨日交易量
                    if df.count()[0] > ma :
                        if df['Adj Close'][-1] < df.tail(ma)['Adj Close'].mean():
                            up.append(symbol.symbol)
                        else:
                            down.append(symbol.symbol)
                    else:
                        raise IndexError(f"{symbol.symbol} {ma} 周期均价因时长不足无法得出\n")     
                else:
                    raise IndexError(f"{symbol.symbol}输入的日期没有数据，请确保输入的日期当天有开市\n")
            except Exception as e:
               err_msg += f"unreachable stock: {symbol.symbol}\nerror message: {e}\n" #把所有无法取得的数据放入msg 并返回给主程序
        return {'up_num':len(up), 'down_num':len(down),'rate':len(up)/(len(up)+len(down)), 'today_volume': today_volume, 'yesterday_volume':yesterday_volume, \
        'percentage':(today_volume - yesterday_volume)/yesterday_volume,'err_msg': err_msg}
