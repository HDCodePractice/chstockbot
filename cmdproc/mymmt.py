from telegram import Update,  BotCommand
from telegram.ext import CommandHandler,  CallbackContext
from json import dumps
from stockutil.ticker import Ticker
import datetime
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup

def mmt_command(update: Update, _: CallbackContext) -> None:
    reply_message = ""
    incoming_message = update.effective_message

    #把消息按空格分割
    msg_l = incoming_message.split(" ")
    if len(msg_l) != 2 and len(msg_l) != 4:
        reply_message = f"请按照 格式1 '/mmt ticker'输入命令，股票代码， \n或者 格式2 '/mmt ticker yyyymmdd yyyymmdd' 输入命令，股票代码，开始时间，结束时间。"
        update.message.reply_text(reply_message)
    else:
        ticker = msg_l[1].lower()
        t = Ticker(ticker, "web","stooq")
        if t.df == None and len(msg_l) == 2:
                reply_message = f"ooops，输入的股票代码好像不存在，请按照格式 '/mmt ticker‘ 重新输入。"
                update.message.reply_text(reply_message)
        else:
            keyboard = [[
                InlineKeyboardButton(text=f"定投一年", callback_data=f"{datetime.date.today() - datetime.timedelta(days=365)},{datetime.date.today()}"),
                InlineKeyboardButton(text=f"定投十年", callback_data=f"{datetime.date.today() - datetime.timedelta(days=3650)},{datetime.date.today()}"),
                InlineKeyboardButton(text=f"自定义时间", callback_data=f"{incoming_message}"),
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(reply_markup)

            # 这里想添加一个5秒后删除这个按钮的消息的命令。 

            if  update.callback_query.data == {incoming_message}:
                reply_message = "请按照格式'/mmt ticker yyyymmdd yyyymmdd' 依次输入命令，股票代码，开始时间，结束时间。"
                update.message.reply_text(reply_message) 
            else:
                startdate,enddate = update.callback_query.data.split(',')
                try:
                    t = Ticker(ticker, "web","stooq",starttime= startdate, endtime=enddate)
                    t.load_data(updateEndtime=True)
                    t.cal_profit()
                    reply_message = t.gen_mmt_msg()
                    update.message.reply_text(reply_message)
                except Exception as err:
                    update.message.reply_text(f"{err}")

        if t.df == None and len(msg_l) == 4:
            reply_message = f"ooops，输入的股票代码好像不存在，请按照格式 '/mmt ticker yyyymmdd yyyymmdd‘ 重新输入。"
            update.message.reply_text(reply_message)
        else:
            ticker = msg_l[1].lower()
            #第四部分是结束时间，切割为年、月、日。如果切割后的日期不存在，设为今天。
            ey,em,ed = msg_l[3][:4],msg_l[3][-4:-2],msg_l[3][-2:]
            if datetime.date(int(ey),int(em),int(ed)):
                enddate = datetime.date(int(ey),int(em),int(ed))
            else:
                enddate = datetime.date.today()

            #第三部分是开始时间，切割为年、月、日。如果切割后的日期不存在，按照结束日期往前推一年。
            sy,sm,sd = msg_l[2][:4],msg_l[2][-4:-2],msg_l[2][-2:]
            if datetime.date(int(sy),int(sm),int(sd)):
                startdate = datetime.date(int(sy),int(sm),int(sd))
            else:
                startdate = enddate - datetime.timedelta(days=365)
            


            try:        
                t = Ticker(ticker, "web","stooq",starttime= startdate, endtime=enddate)
                t.load_data(updateEndtime=True)
                t.cal_profit()
                reply_message = t.gen_mmt_msg()
                if t.starttime == startdate and t.endtime == enddate:
                    update.message.reply_text(reply_message)
                elif t.starttime != startdate or t.endtime != enddate: 
                    reply_message += f"\n{ticker.upper()}的交易日信息为{t.starttime} 至 {t.endtime}" 
                    update.message.reply_text(reply_message)
            except Exception as err:
                update.message.reply_text(f"{err}")

def add_dispatcher(dp):
    dp.add_handler(CommandHandler("mmt", mmt_command))
    return [BotCommand('mmt','试试我的定投')]
