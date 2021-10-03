import pytest
from datetime import datetime,date
import pandas as pd
from stockutil.ticker import Ticker
from telegram import InlineKeyboardButton

def test_mmt_all_para(aapl):
    from cmdproc import mmtcmd
    # 用户会发出所有的参数
    msg = "/mmt aapl 20210801 20210820"
    rmsg = """股票代码：aapl
从2021年08月02日定投 #小毛毛 AAPL，到2021年08月20日累计投入 300元，到昨日市值为 303.84 元，利润为 1.28%
从2021年08月02日定投 #大毛毛 AAPL，到2021年08月20日累计投入 100元，到昨日市值为 101.60 元，利润为 1.60%"""
    buttons = [[
        InlineKeyboardButton("20210801",callback_data="mmt_:aapl:20210801:20210820:uid"),
        InlineKeyboardButton("过去一年",callback_data="mmt_:aapl:20200820:20210820:uid"),
        InlineKeyboardButton("过去10年",callback_data="mmt_:aapl:20110820:20210820:uid")
    ]]
    r,b = mmtcmd.process_income_message(msg,"uid")
    assert b == buttons    
    assert r == rmsg


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

