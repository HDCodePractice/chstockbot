import pytest
from datetime import datetime,date
import pandas as pd
from stockutil.ticker import Ticker

def test_ticker_load_data_web():
    """Test ticker load data."""
    ticker = Ticker("AAPL","web", "stooq")
    df =  ticker.load_data(updateEndtime=True)
    #print(df)
    assert  (date.today() - df.index[-1].date()).days < 7

def test_ticker_load_data_local(shared_datadir):
    """Test ticker load data."""
    ticker = Ticker("AAPL","local", f"{shared_datadir}",starttime=date(2021,1,1),endtime=date(2021,8,20))
    df =  ticker.load_data()
    assert df.index.size == 9315
    assert df.tail(1).index[0] == pd.Timestamp('2021-08-20 00:00:00')
    assert df.head(1).index[0] == pd.Timestamp('1984-09-07 00:00:00')
    ticker = Ticker("GOEV","local", f"{shared_datadir}",starttime=date(2021,1,1),endtime=date(2021,8,20))
    df =  ticker.load_data()
    assert df.index.size == 526
    assert df.tail(1).index[0] == pd.Timestamp('2021-08-20 00:00:00')
    assert df.head(1).index[0] == pd.Timestamp('2019-04-17 00:00:00')

def test_ticker_load_data_local_error(shared_datadir):
    from stockutil.ticker import TickerError
    # axas到8月3日，20号没有交易
    ticker = Ticker("axas","local", f"{shared_datadir}",starttime=date(2021,1,1),endtime=date(2021,8,20))
    with pytest.raises(TickerError) as e:
        ticker.load_data()
    exec_msg = e.value.args[0]
    assert exec_msg == "AXAS:2021-08-20无数据"
    # finw没有数据
    ticker = Ticker("finw","local", f"{shared_datadir}",starttime=date(2021,1,1),endtime=date(2021,8,20))
    with pytest.raises(TickerError) as e:
        ticker.load_data()
    exec_msg = e.value.args[0]
    assert exec_msg == "FINW:2021-08-20无数据"
    # gainz只有0820一天数据
    ticker = Ticker("gainz","local", f"{shared_datadir}",starttime=date(2021,1,1),endtime=date(2021,8,20))
    ticker.load_data()
    assert ticker.df.index.size == 1
    assert ticker.df.index[0] == pd.Timestamp('2021-08-20 00:00:00')
    assert ticker.starttime == date(2021,8,20)


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
    assert exec_msg == "OGN 55 周期均价因时长不足无法得出\n"
    # 低于10周线
    assert goev.symbol_above_moving_average(10) == False
    assert goev.symbol_above_moving_average(100) == False


def test_ticker_cal_profit(shared_datadir):
    """测试定投结果"""
    aapl = Ticker("AAPL", "local", f"{shared_datadir}", starttime=date(2021, 7, 1), endtime=date(2021, 8, 20))
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
    assert xmm_unit * end_price == aapl.xmm_profit["current_price"]
    assert dmm_unit * end_price == aapl.dmm_profit["current_price"]
    assert aapl.xmm_profit["total_principle"] == 700
    assert aapl.dmm_profit["total_principle"] == 200
    assert int(aapl.xmm_profit["profit_percentage"] * 1000000 ) == int(xmm_profit_rate * 1000000)
    assert int(aapl.dmm_profit["profit_percentage"] * 1000000) == int(dmm_profit_rate * 1000000)


def test_cal_symbols_avg(goev,aapl,ogn):
    from stockutil.ticker import TickerError
    ma = aapl.cal_symbols_avg(10)
    assert aapl.smas[10] == 147.81
    ma = aapl.cal_symbols_avg(50)
    print(aapl.smas)
    assert aapl.smas[50] == 142.10559999999998
    ma = ogn.cal_symbols_avg(10)
    assert ogn.smas[10] == 32.52909999999999
    with pytest.raises(TickerError) as e:
        ma = ogn.cal_symbols_avg(100)
    exec_msg = e.value.args[0]
    assert exec_msg == "OGN里的历史数据没有100这么多"

def test_gen_xyh_msg(aapl,goev):
    mas = [10,50,100,200]
    for ma in mas:
        aapl.cal_symbols_avg(ma)
    xyh_msg = aapl.gen_xyh_msg()
    assert xyh_msg == """🟢 10 周期均价：147.81 (0.26%)
🟢 50 周期均价：142.11 (4.28%)
🟢 100 周期均价：135.20 (9.60%)
🟢 200 周期均价：130.47 (13.58%)\n"""

def test_get_today_price_msg(aapl,goev,ogn,shared_datadir):
    msg = aapl.get_today_price_msg()
    assert msg == "AAPL价格: 🟢 148.19 1.02% (146.78 - 148.50):\n"
    msg = goev.get_today_price_msg()
    assert msg == "GOEV价格: 🟢 5.91 1.37% (5.79 - 6.18):\n"
    msg = ogn.get_today_price_msg()
    assert msg == "OGN价格: 🔴 33.22 -1.77% (33.15 - 34.46):\n"
    aapl = Ticker("AAPL", "local", f"{shared_datadir}", endtime=date(2021, 8, 18))
    msg = aapl.get_today_price_msg()
    assert msg == "AAPL价格: 🔴 146.36 -2.55% (146.15 - 150.72):\n"

def test_cal_today_price_rate(aapl,goev):
    #8/20: 148.19
    #8/19: 146.7
    percent,flag = aapl.cal_today_price_rate()
    aapl_percent = (148.19 - 146.7)/146.7 *100 #1.015678254942059
    aapl_flag = "🟢"
    assert percent == aapl_percent
    assert flag == aapl_flag

def test_gen_mmt_msg(aapl,goev):
    aapl.cal_profit()
    aapl.starttime = date(2020,9,4)
    msg = aapl.gen_mmt_msg()
    assert aapl.xmm_profit != None
    assert aapl.dmm_profit != None
    assert msg == """从2020年09月04日定投 #小毛毛 AAPL，到2021年08月20日累计投入 4900元，到昨日市值为 5725.16 元，利润为 16.84%\n从2020年09月04日定投 #大毛毛 AAPL，到2021年08月20日累计投入 1100元，到昨日市值为 1268.71 元，利润为 15.34%\n"""
    # TODO: 找一个时间短的数据做一个assert测试
    

