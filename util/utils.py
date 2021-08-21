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
    return 3

def get_xmm_maxtry(try_date):
    xmm_try_num = 7 - try_date.get_weekday() 
    return xmm_try_num

def get_dmm_maxtry(try_date):
    year = try_date.year
    month = try_date.month
    day = try_date.day
    month_days = calendar.monthrange(year,month)
    dmm_try_num = month_days - day
    return dmm_try_num

def get_date_list(start=None,end=None,freq='W-WED', week_num = 2):
    date_list = pd.date_range(start=start, end=end, freq=freq).tolist()
    date_list['xmm'] = date_list
    for date in date_list:
        if get_week_num(date.year, date.month, date.day) == week_num:
            date_list['dmm'].append(date)
    return date_list

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
  