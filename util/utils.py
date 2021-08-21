import pandas as pd
import datetime


def get_target_date(start=datetime.date.today(),end=datetime.date.today(),freq="W-WED"): #c获得指定日期中的周三 可以扩展成任何天数
    '''
    freq="W-DAY" i.e, W-MON/W-TUE/W-WED/W-THU/W-FRI/W-SAT/W-SUN
    '''
    date_list = pd.date_range(start=start, end=end, freq=freq)
    date_dict = {}
    date_dict["xmm"] =date_list
    date_dict["dmm"] = []

    for date in date_list:
        if is_second_wednesday(date):
            date_dict["dmm"].append(date)
    return date_dict

def is_second_wednesday(d=datetime.date.today()): #计算是否是第二个周三；网上找的，很简单又很有效
    return d.weekday() == 2 and 8 <= d.day <= 15


def sendmsg(bot,chatid,msg,debug=True):
    if debug:
        print(f"{chatid}\n{msg}")
    else:
        bot.send_message(chatid,msg)
