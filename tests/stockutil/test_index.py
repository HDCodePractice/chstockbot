import pytest
from stockutil.index import Index

def test(shared_datadir):
    mytickers = ["AAPL","GOEV","OGN"]
    index = Index("mytickers",f"{shared_datadir}")
    index.tickers = mytickers