import pandas as pd
import getopt
import sys
import datetime, calendar

# TODO 这两个函数是一样的，需要做一个选择
def get_target_date(start=datetime.date.today(),end=datetime.date.today(),freq="W-WED"): #获得指定日期中的周三 可以扩展成任何天数
    """
    freq="W-DAY" i.e, W-MON/W-TUE/W-WED/W-THU/W-FRI/W-SAT/W-SUN
    """
    date_list = pd.date_range(start=start, end=end, freq=freq).tolist()

    date_dict = {}
    date_dict["xmm"] =date_list
    date_dict["dmm"] = []

    for date in date_list:
        if is_second_wednesday(date):
            date_dict["dmm"].append(date)
    return date_dict

# TODO 区别在于week_num，另外date_list是否需要改成list :)  （差别在于 改成list之后，xmm和dmm的数据类型就是一致的）
def get_date_list(start_date=None,end_date=None,freq='W-WED', week_num = 2):
    """
    freq="W-DAY" i.e, W-MON/W-TUE/W-WED/W-THU/W-FRI/W-SAT/W-SUN
    """
    date_list = pd.date_range(start=start_date, end=end_date, freq=freq).tolist()
    date_lists = {}
    date_lists['xmm'] = date_list
    date_lists['dmm'] = []
    for date in date_list:
        if get_week_num(date.year, date.month, date.day) == week_num:
            date_lists['dmm'].append(date)
    return date_lists



def is_second_wednesday(d=datetime.date.today()): #计算是否是第二个周三；网上找的，很简单又很有效
    return d.weekday() == 2 and 8 <= d.day <= 15


def sendmsg(bot,chatid,msg,debug=True):
    if debug:
        print(f"{chatid}\n{msg}")
    else:
        bot.send_message(chatid,msg)

def get_week_num(year:int, month:int, day:int) -> int:
    """
    获取当前日期是本月的第几周
    week_num从1开始
    若第一周不含有周三，则将周数减一。最终获得的是今日所在的周，是本月第二个含有周三的周。
    """
    start = datetime.date(year, month, 1).isocalendar().week #获得当月1号的周数
    end = datetime.date(year, month, day).isocalendar().week #获得当日的周数
    week_num = end - start + 1  #1号所在的周，start 和 end 的周数一样，所以需要 +1
    if datetime.date(year, month, 1).isoweekday() <= 3: #iso计数方法中， 周三的数字是3
        week_num = week_num
    else:
        week_num = week_num - 1 # 1号是周四、周五、周六、周日
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