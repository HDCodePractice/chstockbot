from datetime import datetime, date
import pytest
from stockutil.index import Index

def test_index_get_tickers_list():
    spx = Index("SPX")
    spx.get_tickers_list()
    # print(spx.tickers)
    assert len(spx.tickers) == 505
    assert "AAPL" in spx.tickers
    assert "GOOG" in spx.tickers
    assert "MCD" in spx.tickers

    ndx = Index("NDX")
    ndx.get_tickers_list()
    # print(ndx.tickers)
    assert len(ndx.tickers) == 102
    assert "AAPL" in ndx.tickers
    assert "GOOG" in ndx.tickers
    assert "AMZN" in ndx.tickers    

def test_index_error_symbol():
    from stockutil.index import IndexError
    with pytest.raises(IndexError) as e:
        Index("BBLL")
    exec_msg = e.value.args[0]
    assert exec_msg == "BBLL 不在我们的支持列表中"

def test_index_get_tickers_list_markets(shared_datadir):
    index = Index("nyse",from_s="markets",local_store=f"{shared_datadir}")
    index.get_tickers_list()
    assert len(index.tickers) == 1
    assert "OGN" in index.tickers
    
    index = Index("nasdaq",from_s="markets",local_store=f"{shared_datadir}")
    index.get_tickers_list()
    assert len(index.tickers) == 5
    assert "AAPL" in index.tickers
    assert "GOEV" in index.tickers
    assert "AXAS" in index.tickers

def test_index_error_market_symbol(shared_datadir):
    from stockutil.index import IndexError
    with pytest.raises(IndexError) as e:
        Index("aaaa",from_s="markets",local_store=f"{shared_datadir}")
    exec_msg = e.value.args[0]
    assert exec_msg == "aaaa 不在我们的支持列表中"

def test_market_index_error_symbol(shared_datadir):
    from stockutil.index import IndexError
    with pytest.raises(IndexError) as e:
        Index("BBLL","markets",local_store=f"{shared_datadir}")
    exec_msg = e.value.args[0]
    assert exec_msg == "BBLL 不在我们的支持列表中"


 
def test_index_compare_avg_ma(shared_datadir):
    nasdaq = Index("nasdaq","markets",local_store=f"{shared_datadir}",endtime=date(2021,8,20))
    nasdaq.get_tickers_list()
    nasdaq.compare_avg_ma(10)
    assert len(nasdaq.down) == 1
    assert 'GOEV' in nasdaq.down
    assert len(nasdaq.up) == 1
    assert 'AAPL' in nasdaq.up
    nasdaq.compare_avg_ma(100)
    assert len(nasdaq.down) == 1
    assert 'GOEV' in nasdaq.down
    assert len(nasdaq.up) == 1
    assert 'AAPL' in nasdaq.up

def test_index_compare_avg_ma_error(shared_datadir):
    nyse = Index("nyse","markets",local_store=f"{shared_datadir}",endtime=date(2021,8,20))
    nyse.get_tickers_list()
    nyse.compare_avg_ma(100)
    assert len(nyse.down) == 0
    assert len(nyse.up) == 0
    # print(nyse.tickers,nyse.down,nyse.up,nyse.err_msg)
    assert nyse.err_msg == "nyse OGN 100 周期均价因时长不足无法得出\n\n"


def test_gen_index_msg(shared_datadir):
    nasdaq = Index("nasdaq","markets",local_store=f"{shared_datadir}",endtime=date(2021,8,20))
    nasdaq.get_tickers_list()
    nasdaq.compare_avg_ma(10)
    msg = nasdaq.gen_index_msg()
    assert msg == "nasdaq共有2支股票，共有50.00%高于10周期均线\n当日交易量变化：-30.74%\n"

def test_compare_market_volume(shared_datadir):
    nasdaq = Index("nasdaq","markets",local_store=f"{shared_datadir}",endtime=date(2021,8,20))
    msg = nasdaq.compare_market_volume()
    today_g = 2383633
    today_a = 60549630
    yes_g = 3907327
    yes_a = 86960310
    rate = (today_a+today_g)/(yes_a+yes_g)-1
    assert msg == f'{"nasdaq".upper()}市场较前一日交易量的变化为{(rate)*100:.2f}%\n'
    nyse = Index("nyse","markets",local_store=f"{shared_datadir}",endtime=date(2021,8,20))
    msg = nyse.compare_market_volume()
    today_o = 2354628
    yes_o = 2522056
    rate = (today_o)/(yes_o)-1
    assert msg == f'{"nyse".upper()}市场较前一日交易量的变化为{(rate)*100:.2f}%\n'

def test_compare_market_volume_error(shared_datadir):
    nasdaq = Index("nasdaq","markets",local_store=f"{shared_datadir}",endtime=date(2021,8,20))
    nasdaq.compare_market_volume()
    assert nasdaq.err_msg == "AXAS GAINZ FINW 2021-08-20无数据"