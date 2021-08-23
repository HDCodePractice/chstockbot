import pandas as pd
import getopt
import sys
import datetime, calendar



def help():
    return "'utils.py -c <configpath>'"

def sendmsg(bot,chatid,msg,debug=True):
    if debug:
        print(f"{chatid}\n{msg}")
    else:
        bot.send_message(chatid,msg)

def get_week_num(year, month, day):
    """
    获取当前日期是本月的第几周
    """
    start = int(datetime.date(year, month, 1).strftime("%W"))
    end = int(datetime.date(year, month,day).strftime("%W"))
    week_num = end - start + 1
    return week_num

def get_default_maxtry(try_date):
    """
    获取缺省的最大尝试天数
    """
    return 3

def get_xmm_maxtry(try_date):
    """
    获取xmm的最大尝试天数
    """
    try_date = try_date.date()
    xmm_try_num = 5 - try_date.weekday() 
    return xmm_try_num

def get_dmm_maxtry(try_date):
    """
    获取dmm的最大尝试天数
    """
    year = try_date.year
    month = try_date.month
    day = try_date.day
    month_days = calendar.monthrange(year,month)
    dmm_try_num = month_days[1] - day
    return dmm_try_num

def get_date_list(start_date=None,end_date=None,freq='W-WED', week_num = 2):
    date_list = pd.date_range(start=start_date, end=end_date, freq=freq)
    date_lists = {}
    date_lists['xmm'] = date_list
    date_lists['dmm'] = []
    for date in date_list:
        if get_week_num(date.year, date.month, date.day) == week_num:
            date_lists['dmm'].append(date)
    return date_lists

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:", ["config="])
    except getopt.GetoptError:
        print(help())
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(help())
            sys.exit()

# a = get_date_list(start_date=datetime.date(2021,1,1), end_date=datetime.date.today(), freq='W-WED', week_num = 2)

# date = a['xmm'][0]

# b = get_xmm_maxtry(date)

# print (date)
# print (date.weekday())
# print (b)
