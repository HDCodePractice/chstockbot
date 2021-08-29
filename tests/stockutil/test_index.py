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