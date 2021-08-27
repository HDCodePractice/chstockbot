import pytest
from datetime import datetime
import pandas as pd
from stockutil.ticker import Ticker

def test_ticker_load_data_web():
    """Test ticker load data."""
    ticker = Ticker("AAPL","web", "stooq")
    df =  ticker.load_data()
    # print(df)
    assert df.index.size > 200

def test_ticker_load_data_local(shared_datadir):
    """Test ticker load data."""
    ticker = Ticker("AAPL","local", f"{shared_datadir}")
    df =  ticker.load_data()
    assert df.index.size == 9315
    assert df.tail(1).index[0] == pd.Timestamp('2021-08-20 00:00:00')
    assert df.head(1).index[0] == pd.Timestamp('1984-09-07 00:00:00')

def test_ticker_symbol_above_moving_average(ogn,goev):
    """Test ticker symbol above moving average."""
    from stockutil.ticker import maNotEnoughError
    # 高于10周线
    assert ogn.symbol_above_moving_average(10) == True
    assert ogn.symbol_above_moving_average(20) == True
    # 不足55周线计算
    with pytest.raises(maNotEnoughError) as e:
        assert ogn.symbol_above_moving_average(55) == True
    exec_msg = e.value.args[0]
    assert exec_msg == "55 周期均价因时长不足无法得出\n"
    # 低于10周线
    assert goev.symbol_above_moving_average(10) == False
    assert goev.symbol_above_moving_average(100) == False