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
    assert len(index.tickers) == 2
    assert "AAPL" in index.tickers
    assert "GOEV" in index.tickers

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

def test_index_get_market_ticker_list(shared_datadir):
    nasdaq = Index("nasdaq","markets",local_store=f"{shared_datadir}")
    nasdaq.get_tickers_list()
    # print(nasdaq.tickers)
    assert len(nasdaq.tickers) == 2
    assert "AAPL" in nasdaq.tickers
    assert "GOEV" in nasdaq.tickers

    nyse = Index("nyse","markets",local_store=f"{shared_datadir}")
    nyse.get_tickers_list()
    # print(nyse.tickers)
    assert len(nyse.tickers) == 1
    assert "OGN" in nyse.tickers
 
def test_index_compare_avg_ma(shared_datadir):
    nasdaq = Index("nasdaq","markets",local_store=f"{shared_datadir}")
    nasdaq.get_tickers_list()
    nasdaq.compare_avg_ma(10,date(2021,8,20))
    assert len(nasdaq.down) == 1
    assert 'GOEV' in nasdaq.down
    assert len(nasdaq.up) == 1
    assert 'AAPL' in nasdaq.up
    nasdaq.compare_avg_ma(100,date(2021,8,20))
    assert len(nasdaq.down) == 1
    assert 'GOEV' in nasdaq.down
    assert len(nasdaq.up) == 1
    assert 'AAPL' in nasdaq.up

def test_index_compare_avg_ma_error(shared_datadir):
    nyse = Index("nyse","markets",local_store=f"{shared_datadir}")
    nyse.get_tickers_list()
    nyse.compare_avg_ma(100,date(2021,8,20))
    assert len(nyse.down) == 0
    assert len(nyse.up) == 0
    # print(nyse.tickers,nyse.down,nyse.up,nyse.err_msg)
    assert nyse.err_msg == "nyse OGN 100 周期均价因时长不足无法得出\n"


def test_gen_index_msg(shared_datadir):
    nasdaq = Index("nasdaq","markets",local_store=f"{shared_datadir}")
    nasdaq.get_tickers_list()
    nasdaq.compare_avg_ma(10,date(2021,8,20))
    msg = nasdaq.gen_index_msg(date(2021,8,20))
    assert msg == "nasdaq共有2支股票，共有50.00%高于10周期均线\n当日交易量变化：-30.74%\n"