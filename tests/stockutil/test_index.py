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