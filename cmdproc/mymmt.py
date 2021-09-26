from telegram import Update,  BotCommand
from telegram.ext import CommandHandler,  CallbackContext
from json import dumps
from stockutil.ticker import Ticker
import datetime


def mmt_command(update: Update, _: CallbackContext) -> None:
    reply_message = ""
    incoming_message = update.effective_message
    
    #把消息按照空格分割, 期待分成4份
    msg_l = incoming_message.split(" ")
    if len(msg_l) != 4:
        reply_message = "请按照格式 '/mmt ticker yyyymmdd yyyymmdd' 输入命令，股票代码，开始时间，结束时间。"
        update.message.reply_text(reply_message)
    else:        
        #第二部分是ticker name
        ticker = msg_l[1].lower()
        #第三部分是开始时间，切割为年、月、日
        sy,sm,sd = msg_l[2][:4],msg_l[2][-4:-2],msg_l[2][-2:]
        if datetime.date(int(sy),int(sm),int(sd)):
            startdate = datetime.date(int(sy),int(sm),int(sd))
        else:
            startdate = datetime.date.today() - datetime.timedelta(days=365)
        #第四部分是结束时间，切割为年、月、日
        ey,em,ed = msg_l[3][:4],msg_l[3][-4:-2],msg_l[3][-2:]
        if datetime.date(int(ey),int(em),int(ed)):
            enddate = datetime.date(int(ey),int(em),int(ed))
        else:
            enddate = datetime.date.today()

        try:        
            t = Ticker(ticker, "web","stooq",starttime= startdate, endtime=enddate)
            t.load_data()
            t.cal_profit()
            reply_message = t.gen_mmt_msg()
            if t.starttime == startdate and t.endtime == enddate:
               update.message.reply_text(reply_message)
            elif t.starttime != startdate or t.endtime != enddate:  # 这里要处理的好的，好像还要改造tikcer
                reply_message += f"\n{ticker.upper()}的交易日信息为{t.starttime} 至 {t.endtime}" 
        except Exception as err:
            update.message.reply_text(f"{err}")


def add_dispatcher(dp):
    dp.add_handler(CommandHandler("mmt", mmt_command))
    return [BotCommand('mmt','试试我的定投')]
