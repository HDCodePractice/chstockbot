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


def test_ticker_cal_profit(shared_datadir):
    """测试定投结果"""
    aapl = Ticker("AAPL", "local", f"{shared_datadir}", starttime=datetime(2021, 7, 1), endtime=datetime(2021, 8, 20))
    aapl.load_data()
    xmm = [
        [datetime(2021,7,7),144.35],
        [datetime(2021,7,14),148.93],
        [datetime(2021,7,21),145.18],
        [datetime(2021,7,28),144.76],
        [datetime(2021,8,4),146.73],
        [datetime(2021,8,11),145.86],
        [datetime(2021,8,18),146.36]
        ]
    dmm = [[datetime(2021,7,14),148.93],[datetime(2021,8,11),145.86]]
    # xmm 每次买100元的股数累计
    xmm_unit = 0
    for i in xmm:
        xmm_unit += 100 / i[1]
    # dmm 每次买100元的股数累计
    dmm_unit = 0
    for i in dmm:
        dmm_unit += 100 / i[1]
    # 8月20日价格 148.19
    end_price = aapl.df.loc[datetime(2021,8,20),"Close"]
    assert end_price == 148.19
    # 利润率：
    xmm_profit_rate = ( xmm_unit * end_price - 700) / 700
    dmm_profit_rate = ( dmm_unit * end_price - 200) / 200
    aapl.cal_profit()
    print("xmm",aapl.xmm_profit,"dmm",aapl.dmm_profit)
    # xmm {'current_profit': 710.4488392607637, 'total_principle': 700, 'profit_percentage': 0.014926913229662553} 
    # dmm {'current_profit': 201.10054445786588, 'total_principle': 200, 'profit_percentage': 0.005502722289329354}
    assert xmm_unit * end_price == aapl.xmm_profit["current_profit"]
    assert dmm_unit * end_price == aapl.dmm_profit["current_profit"]
    assert aapl.xmm_profit["total_principle"] == 700
    assert aapl.dmm_profit["total_principle"] == 200
    assert aapl.xmm_profit["profit_percentage"] == xmm_profit_rate
    assert aapl.dmm_profit["profit_percentage"] == dmm_profit_rate