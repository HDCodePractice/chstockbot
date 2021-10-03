import pytest
from stockutil.ticker import Ticker
from datetime import date

@pytest.fixture
def aapl(shared_datadir):
    ticker = Ticker("AAPL","local", f"{shared_datadir}",endtime=date(2021,8,20))
    ticker.load_data()
    return ticker

@pytest.fixture
def ogn(shared_datadir):
    ticker = Ticker("OGN","local", f"{shared_datadir}",endtime=date(2021,8,20))
    ticker.load_data()
    return ticker

@pytest.fixture
def goev(shared_datadir):
    ticker = Ticker("GOEV","local", f"{shared_datadir}",endtime=date(2021,8,20))
    ticker.load_data()
    return ticker