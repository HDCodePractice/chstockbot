import pytest
from datetime import datetime,date
import pandas as pd
from stockutil.ticker import Ticker

def test_mmt_all_para(aapl):
    # 用户会发出所有的参数
    msg = "/mmt aapl 20210101 20210820"

def test_mmt_3para(aapl):
    # 用户会发出三个参数
    msg = "/mmt aapl 20210101"

def test_mmt_2para(aapl):
    # 用户会发出两个参数
    msg = "/mmt aapl"


def test_mmt_1para(aapl):
    # 用户会发出一个参数
    msg = "/mmt"

def test_mmt_error():
    # 用户会发出错误的参数
    # 多发出一个参数
    msg = "/mmt aapl 20210101 20210820 20210820"
    # 发出错误的end date
    msg = "/mmt aapl 20210101 20210920"
    # 发出错误的start date
    msg = "/mmt aapl 10101 20210920"

