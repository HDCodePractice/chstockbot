from telegram import Update,  BotCommand
from telegram.ext import CommandHandler,  CallbackContext
from json import dumps
from stockutil.ticker import Ticker


def mmt_command(update: Update, _: CallbackContext) -> None:
    reply_message = ""
    incoming_message = update.effective_message
    msg_l = incoming_message.split(" ")
    if len(msg_l) != 4:
        reply_message = "请按照格式 '/mmt ticker yyyymmdd yyyymmdd' 输入命令，股票代码，开始时间 和 结束时间。"
        update.message.reply_text(reply_message)
    else:
        ticker = msg_l[1].lower()
        startdate = msg_l[2]
        enddate = msg_l[3]
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
