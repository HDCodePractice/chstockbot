from datetime import datetime
import pandas as pd

def test_ticker_load_data_web():
    """Test ticker load data."""
    from stockutil.ticker import Ticker
    ticker = Ticker("AAPL","web", "stooq")
    df =  ticker.load_data()
    # print(df)
    assert df.index.size > 200

def test_ticker_load_data_local(shared_datadir):
    """Test ticker load data."""
    from stockutil.ticker import Ticker
    ticker = Ticker("AAPL","local", f"{shared_datadir}")
    df =  ticker.load_data()
    print(df)
    assert df.index.size == 9315
    assert df.tail(1).index[0] == pd.Timestamp('2021-08-20 00:00:00')