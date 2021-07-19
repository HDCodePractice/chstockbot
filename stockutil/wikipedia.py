import datetime
import pickle
import datetime
from numpy import msort
import pandas as pd

# import requests
# import bs4 as bs
# def get_sp500_tickers():
#     resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
#     soup = bs.BeautifulSoup(resp.text, 'lxml')
#     table = soup.find('table', {'class': 'wikitable sortable'})
#     tickers = []
#     for row in table.findAll('tr')[1:]:
#         ticker = row.findAll('td')[0].text[:-1]
#         tickers.append(ticker)
#     return tickers

def get_sp500_tickers():
    table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    df = table[0]
    return df['Symbol'].tolist()

def get_ndx100_tickers():
    table = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')
    df = table[3]
    return df['Ticker'].tolist() 
    # table = pd.read_html('https://dailypik.com/nasdaq-100-companies/')
    # df = table[0]
    # return df['Symbol'].tolist() 

def save_list(list,filename):
    # with open("sp500tickers.pickle", "wb") as f:
    #     pickle.dump(tickers, f)
    with open(filename, "wb") as f:
        pickle.dump(list, f)

def load_list(filename):
    tickers = []
    with open(filename, "rb") as f:
        tickers = pickle.load(f)
    return tickers

if __name__ == '__main__':
    import stooq
    # 本程序只是用于测试，正常使用请from stockutil import wikipedia
    sp500 = get_sp500_tickers()
    ndx100 = get_ndx100_tickers()
    #save_list(sp500,"sp500.pickle")
    #save_list(ndx100,"ndx100.pickle")
    indexes = {"sp500": sp500, "ndx100": ndx100}

    for key in indexes:
        print(key)
        up = []
        down = []       
        for symbol in indexes[key]:
            try:
                if stooq.symbol_above_moving_average(symbol,end=datetime.datetime.strptime("20210716","%Y%m%d").date()):
                    up.append(symbol)
                else:
                    down.append(symbol)
            except Exception as e:
                print(f"unreachable stock: {symbol}\nerror message: {e}\n")
        print(f"{key}共有{len(up)+len(down)}支股票，共有{len(up)/(len(up)+len(down))*100:.2f}%高于50周期均线")
