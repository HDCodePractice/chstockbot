import getopt,sys,config,os

from numpy import e
from requests.sessions import extract_cookies_to_jar
import pandas_datareader.data as web
import datetime
import pandas as pd
from telegram import Bot
from pandas_datareader._utils import RemoteDataError
from requests.exceptions import ConnectionError
from stockutil import stooq, wikipedia
from sendxyh import sendmsg

def help():
    return "'sendxyh.py -c configpath -s yyyymmdd -e yyyymmdd'"

def cal_mmt_profit(symbol,ds,principle=100,start=datetime.date.today(),end=datetime.date.today()):
    err_msg = "" #定义错误信息
    dmm_stock_number = 0 #初始化 大毛毛股数
    xmm_stock_number = 0 #初始化 小毛毛股数
    xmm_msg ="" #定义大毛毛信息
    dmm_msg ="" #定义小毛毛信息
    #获得指定日期中所有的周三
    xmm_profit_arr = []
    dmm_profit_arr = []
    date_list = pd.date_range(start=start, end=end, freq='W-WED').strftime('%Y-%m-%d').tolist()
    second_wednesday_count = 0 #初始化 大毛毛每月第二个周三的个数
    for datasource in ds:
        try:
            df = web.DataReader(symbol.upper(), datasource,start=start,end=end)
            df = df.sort_values(by="Date") #将排序这个步骤放在了判断df是否存在之后
            for date in date_list:
                price = df.loc[date,"Close"] #获取周三当日的收盘价
                if is_second_wednesday(datetime.datetime.strptime(date, "%Y-%m-%d")):
                    second_wednesday_count +=1 #如果当天是当月第二个周三，大毛毛个数+1
                    dmm_stock_number += principle/price #获取大毛毛股数
                    dmm_profit_arr.append({"date":date,"symbol":symbol,"price":price,"stock_number": principle/price})
                xmm_stock_number += principle/price #获取小毛毛股数
                xmm_profit_arr.append({"date":date,"symbol":symbol,"price":price,"stock_number": principle/price})
            xmm_profit = {"current_price": df["Close"][-1], "current_profit":xmm_stock_number * df["Close"][-1]} #计算当日小毛毛获利
            dmm_profit = {"current_price": df["Close"][-1], "current_profit":dmm_stock_number * df["Close"][-1]} #计算当日大毛毛获利
            xmm_msg = f"如果你从{start.strftime('%Y年%m月%d日')}定投 #小毛毛 {symbol} {principle}元，到{end.strftime('%Y年%m月%d日')}累计投入 {principle * len(date_list)}元，到昨日市值为 {xmm_profit['current_profit']:0.2f} 元，累计利润为 {(1 - principle * len(date_list)/xmm_profit['current_profit'])*100:0.2f}%\n"
            dmm_msg = f"如果你从{start.strftime('%Y年%m月%d日')}定投 #大毛毛 {symbol} {principle}元，到{end.strftime('%Y年%m月%d日')}累计投入 {principle * second_wednesday_count}元，到昨日市值为 {dmm_profit['current_profit']:0.2f} 元，累计利润为 {(1 - principle * second_wednesday_count/dmm_profit['current_profit'])*100:0.2f}%\n"

            break #当数据源成功读取并处理数据后，从当前程序break并返回信息； 防止程序运行所有的数据源
        except NotImplementedError:
            err_msg += f"当前数据源{datasource}不可用"
            continue
        except RemoteDataError:
            err_msg += f"在{datasource}找不到{symbol}的信息\n"
            continue
        except Exception as e: 
            err_msg += f"当前{symbol}读取报错了，具体错误信息是{e}\n"
            continue 
    #print(f"小毛毛数据：{xmm_profit_arr}\n,大毛毛数据：{dmm_profit_arr}\n,小毛毛当日收盘价:{xmm_profit}\n,大毛毛当日收盘价：{dmm_profit}\n") #测试用数据
    return xmm_msg,dmm_msg,err_msg


def get_wednesday_date(start=datetime.date.today(),end=datetime.date.today()): #c获得指定日期中的周三 可以扩展成任何天数
    date_list = pd.date_range(start=start, end=end, freq='W-WED').strftime('%Y-%m-%d').tolist()
    return date_list

def is_second_wednesday(d=datetime.date.today()): #计算是否是第二个周三；网上找的，很简单又很有效
    return d.weekday() == 2 and 8 <= d.day <= 15

def generate_mmt_msg(): #生成定投信息
    chat_msg = ""
    if is_second_wednesday():
        chat_msg = f"如果你每月定投，哪么今天是投 #大毛毛 的日子啦，今天是本月第二周的周三 请向小🐷🐷中塞入你虔诚的💰吧～\n如果你每周定投，今天依然是投 #小毛毛 的日子 放入🪙，哪么今天照常放入虔诚的🪙吧～\n"
    
    else:
        chat_msg = f"如果你每周定投，哪么今天是投 #小毛毛 的日子啦，今天是周三 请向小🐷🐷中塞入你虔诚的🪙吧～\n"
    return chat_msg




if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:s:e:", ["config=","starttime=","endtime="])
    except getopt.GetoptError:
        print(help())
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(help())
            sys.exit()
        elif opt in ("-c", "--config"):
            config.config_path = arg  
        elif opt in ("-s", "--starttime"): #setup datetime format "yyyymmdd"
            try: #尝试对从参数中读取的日期进行日期格式转换，如果没有参数，则使用1/26/2021
                start_time = datetime.datetime.strptime(arg,"%Y%m%d").date()
            except:
                print(f"无法读取日期：\n{help()}")
                sys.exit(2)
        elif opt in ("-e", "--endtime"):
            try: #尝试对从参数中读取的日期进行日期格式转换，如果没有参数，则使用1/26/2021
                end_time = datetime.datetime.strptime(arg,"%Y%m%d").date()
            except:
                print(f"无法读取日期：\n{help()}")
                sys.exit(2)

        

    config.config_file = os.path.join(config.config_path, "config.json")
    try:
        CONFIG = config.load_config()
    except FileNotFoundError:
        print(f"config.json not found.Generate a new configuration file in {config.config_file}")
        config.set_default()
        sys.exit(2)

    bot = Bot(token = CONFIG['Token'])
    symbols = CONFIG['mmtticker']
    adminchat = CONFIG['xyhlog']
    debug = CONFIG['DEBUG']
    ds = CONFIG['xyhsource']   
    mmtchat = CONFIG['mmtchat'] 
    mmtstartdate = CONFIG['mmtstartdate']
    mmt_message = ""
    admin_message = ""
    target_end_time = datetime.date.today()
    target_start_time = datetime.date(2021,1,1)
    try: 
        target_end_time= end_time
    except:
        target_end_time
    try:
        target_start_time = start_time
    except:
        target_start_time
    chat_msg = generate_mmt_msg()
    mmt_message += chat_msg
    try:
        for symbol in symbols:#start日期设置为2021/5/26， 可以使用参数来进行定义（to do)
            dmm_msg,xmm_msg, err_msg = cal_mmt_profit(symbol,ds,start=target_start_time,end=target_end_time)
            if dmm_msg:
                mmt_message += dmm_msg
            if xmm_msg:
                mmt_message += xmm_msg               
            if err_msg:
                admin_message += err_msg
            
        if mmt_message:
            sendmsg(bot,mmtchat,mmt_message,debug)
        if admin_message:
            sendmsg(bot,adminchat,admin_message,debug)
    except Exception as err:
        sendmsg(bot,adminchat,f"今天完蛋了，什么都不知道，快去通知管理员，bot已经废物了，出的问题是:\n{type(err)}:\n{err}",debug)
    
    