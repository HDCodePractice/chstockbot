import pytest
from datetime import datetime,date,timedelta
import pandas as pd
from stockutil.ticker import Ticker
from telegram import InlineKeyboardButton
from cmdproc import mmtcmd


def test_mmt_all_para(aapl):
    # 用户会发出所有的参数
    msg = "/mmt aapl 20210801 20210820"
    button_reply = """股票代码：aapl\n请选择想要进行毛毛投利润率计算的日期：\n"""
    rmsg = """由于起始日期2021-08-01的数据不存在，自动转为最近的有数据的日期:2021-08-02
从2021年08月02日定投 #小毛毛 AAPL，到2021年08月20日累计投入 300元，到昨日市值为 303.84 元，利润为 1.28%
从2021年08月02日定投 #大毛毛 AAPL，到2021年08月20日累计投入 100元，到昨日市值为 101.60 元，利润为 1.60%\n"""
    buttons = [[
        InlineKeyboardButton(f"20210801",callback_data=f"aapl:2021-08-01:2021-08-20:uid"),
        InlineKeyboardButton(f"过去一年",callback_data=f"aapl:2020-08-20:2021-08-20:uid"),
        InlineKeyboardButton(f"过去10年",callback_data=f"aapl:2011-10-19:2021-08-20:uid")
    ]]
    r,b = mmtcmd.process_income_message(msg,"uid")
    profit_msg = mmtcmd.process_ticker_profit("aapl","2021-08-01","2021-08-20")
    #assert b == buttons
    assert r == button_reply   
    assert rmsg == profit_msg


def test_mmt_3para(aapl):
    # 用户会发出三个参数
    msg = "/mmt aapl 20210101"
    button_reply = f"由于未检测到或只检测到部分日期参数，毛毛投即将使用的日期参数为:2021-01-01/{datetime.today().date()}\n股票代码：aapl\n请选择想要进行毛毛投利润率计算的日期：\n"
    rmsg = """由于起始日期2021-01-01的数据不存在，自动转为最近的有数据的日期:2021-01-04
从2021年01月04日定投 #小毛毛 AAPL，到2021年08月20日累计投入 3300元，到昨日市值为 3716.19 元，利润为 12.61%
从2021年01月04日定投 #大毛毛 AAPL，到2021年08月20日累计投入 800元，到昨日市值为 898.78 元，利润为 12.35%\n"""
    buttons = [[
        InlineKeyboardButton(f"20210801",callback_data=f"aapl:2021-01-01:2021-08-20:uid"),
        InlineKeyboardButton(f"过去一年",callback_data=f"aapl:2020-08-20:2021-08-20:uid"),
        InlineKeyboardButton(f"过去10年",callback_data=f"aapl:2011-10-19:2021-08-20:uid")
    ]]
    r,b = mmtcmd.process_income_message(msg,"uid")
    profit_msg = mmtcmd.process_ticker_profit("aapl","2021-01-01","2021-08-20")
    #assert b == buttons
    assert r == button_reply   
    assert rmsg == profit_msg

def test_mmt_2para(aapl):
    # 用户会发出两个参数
    msg = "/mmt aapl"
    button_reply = f"由于未检测到或只检测到部分日期参数，毛毛投即将使用的日期参数为:{datetime.today().date()-timedelta(days=365)}/{datetime.today().date()}\n股票代码：aapl\n请选择想要进行毛毛投利润率计算的日期：\n"

    rmsg = """由于起始日期2021-08-01的数据不存在，自动转为最近的有数据的日期:2021-08-02
从2021年08月02日定投 #小毛毛 AAPL，到2021年08月20日累计投入 300元，到昨日市值为 303.84 元，利润为 1.28%
从2021年08月02日定投 #大毛毛 AAPL，到2021年08月20日累计投入 100元，到昨日市值为 101.60 元，利润为 1.60%\n"""
    buttons = [[
        InlineKeyboardButton(f"20210801",callback_data=f"aapl:20210801:20210820:uid"),
        InlineKeyboardButton(f"过去一年",callback_data=f"aapl:20200820:20210820:uid"),
        InlineKeyboardButton(f"过去10年",callback_data=f"aapl:20111019:20210820:uid")
    ]]
    r,b = mmtcmd.process_income_message(msg,"uid")
    #assert b == buttons
    assert r == button_reply   
    #assert rmsg == mmtcmd.profit_list["1"]


def test_mmt_1para(aapl):
    # 用户会发出一个参数
    msg = "/mmt"
    r,b = mmtcmd.process_income_message(msg,"uid")
    assert r == "输入格式不对，请使用 /mmt appl 20210101 20210820这样的格式查询，日期格式为yyyymmdd"
def test_mmt_error():
    # 用户会发出错误的参数
    # 多发出一个参数
    msg = "/mmt aapl 20210101 20210820 20210820"
    r,b = mmtcmd.process_income_message(msg,"uid")
    assert r == "输入格式不对，请使用 /mmt appl 20210101 20210820这样的格式查询，日期格式为yyyymmdd"
    assert b == None
    # 发出错误的start date
    msg = "/mmt aapl 10101 20210920"
    r,b = mmtcmd.process_income_message(msg,"uid")
    assert r == "输入格式不对，请使用 /mmt appl 20210101 20210820这样的格式查询，日期格式为yyyymmdd"
    assert b == None
    # 发出错误的start date
    msg = "/mmt aapl 10101"
    r,b = mmtcmd.process_income_message(msg,"uid")
    assert r == "输入格式不对，请使用 /mmt appl 20210101 20210820这样的格式查询，日期格式为yyyymmdd"
    assert b == None
    # 发出错误的start date
    msg = "/mmt aapl 10101 10101"
    r,b = mmtcmd.process_income_message(msg,"uid")
    assert r == "输入格式不对，请使用 /mmt appl 20210101 20210820这样的格式查询，日期格式为yyyymmdd"
    assert b == None
    # 不存在的股票代码
    msg = "/mmt aapla"
    r,b = mmtcmd.process_income_message(msg,"uid")
    assert r == "aapla股票代码不存在，也许我的数据中不存在这样的股票，请使用我知道的股票代码查询（当然也有可能是系统出错啦，你就晚点再查吧～）"
    assert b == None
    # 不存在的股票代码
    msg = "/mmt 20010101 aapl"
    r,b = mmtcmd.process_income_message(msg,"uid")
    assert r == "20010101股票代码不存在，也许我的数据中不存在这样的股票，请使用我知道的股票代码查询（当然也有可能是系统出错啦，你就晚点再查吧～）"
    assert b == None    
    # 发出错误的end date
    # msg = "/mmt aapl 20210101 20210920"
    # r,b = mmtcmd.process_income_message(msg,"uid")
    # assert r == "最后一个交易日是20210820，请输入一个有效的截止日期"
    # assert b == None

