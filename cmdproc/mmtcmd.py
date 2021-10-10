from telegram import Update,  BotCommand,ParseMode
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from json import dumps
from stockutil.ticker import Ticker, TickerError
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
import datetime
from config import ENV
from util.tgutil import delay_del_msg

admingroup = ENV.ADMIN_GROUP
groups = ENV.GROUPS
admins = ENV.ADMINS

reply_msg = f"输入格式不对，请使用 /mmt appl 20210101 20210820这样的格式查询，日期格式为yyyymmdd"  
profit_list = {}

def process_income_message(incoming_message, user):
    #reply_message,keyboard = process_income_message(incoming_message, user)
    ten_year_date = datetime.datetime.today().date() - datetime.timedelta(days=3650)
    one_year_date = datetime.datetime.today().date() - datetime.timedelta(days=365)
    mmt_starttime = datetime.datetime.today().date() - datetime.timedelta(days=365)
    mmt_endtime = datetime.datetime.today().date()
    #profit_list = {} #重置dict
    msg_text = ""
    msg_l = incoming_message.split(" ")
    if len(msg_l) <= 1 or len(msg_l) > 4:
        return reply_msg,None
    #处理日期，如果只有部分有效日期，自动更新成一年前的今天的日期到今天的日期 
    try:       
        mmt_starttime =  datetime.datetime.strptime(msg_l[2],"%Y%m%d").date()
        mmt_endtime = datetime.datetime.strptime(msg_l[3],"%Y%m%d").date()
    except ValueError:
        return reply_msg,None
    except IndexError:
        msg_text += f"由于未检测到或只检测到部分日期参数，毛毛投即将使用的日期参数为:{mmt_starttime}/{mmt_endtime}\n"
    except Exception:
        return reply_msg,None
    #处理毛毛投利润
    try:
        count = 1
        for i in [mmt_starttime, one_year_date,ten_year_date]:
            profit_list[f"{count}"] = process_ticker_profit(msg_l[1].lower(),i,mmt_endtime)
            count +=1

    except TickerError:
        msg_text = f"{msg_l[1].lower()}股票代码不存在，也许我的数据中不存在这样的股票，请使用我知道的股票代码查询（当然也有可能是系统出错啦，你就晚点再查吧～）"
        return msg_text, None
    except Exception as err:
        msg_text = f"数据正在更新中；请稍后再试; {err}"
        return msg_text, None
    #准备返回3个按钮； 传入profit_list里的key 和用户名
    keyboard = [[
        InlineKeyboardButton(text=f"{mmt_starttime}", callback_data=f"1:{user}"),
        InlineKeyboardButton(text=f"过去一年", callback_data=f"2:{user}"),
        InlineKeyboardButton(text=f"过去10年", callback_data=f"3:{user}")
    ]]
    msg_text += f"股票代码：{msg_l[1].lower()}\n请选择想要进行毛毛投利润率计算的日期：\n"
    return msg_text, keyboard

def process_ticker_profit(ticker,starttime,endtime): #计算利润率的函数
    reply_txt = ""
    t = Ticker(ticker, "web","stooq",starttime= starttime, endtime=endtime)
    t.xmm_price_list = {}
    t.dmm_price_list = {}
    t.price_list = {}
    t.load_data(updateEndtime=True)
    if t.starttime != starttime:
        reply_txt += f"由于起始日期{starttime}的数据不存在，自动转为最近的有数据的日期:{t.starttime}\n"
    if t.endtime != endtime:
        reply_txt += f"由于结束日期{endtime}的数据不存在，自动转为最近的有数据的日期:{t.endtime}\n"
    t.cal_profit()
    reply_txt += t.gen_mmt_msg()
    return reply_txt

def mmt_command(update: Update, context: CallbackContext) -> None:
    incoming_message = update.effective_message
    user = incoming_message.from_user.id
    reply_message,keyboard = process_income_message(incoming_message.text, user)
    if keyboard == None:
        incoming_message.reply_text(reply_message)
        return
    reply_markup = InlineKeyboardMarkup(keyboard)
    #incoming_message.reply_markdown_v2(text=reply_message.replace("-", "\-"),reply_markup=reply_markup)
    context.bot.send_message(chat_id=incoming_message.chat_id, text=reply_message.replace("-", "\-"), reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)

def announce_mmt(update: Update, context:CallbackContext):
    #获取点击按钮的用户信息和毛毛投信息
    reply_user_id = update.effective_chat.id
    reply_user_name = update.effective_chat.full_name
    mmt_data = update.callback_query.data.split(":")
    chat_id = update.effective_chat.id
    #如果不是提问人的id， 回复信息
    alert_msg = f"亲爱的{reply_user_name}, 这个不是你提的问题，请不要随意点击！如果想要查询毛毛投的信息，请自己输入命令！"
    if reply_user_id != int(mmt_data[1]):
        context.bot.send_message(chat_id,alert_msg)
        return
    #直接读取profit_list里的value
    for key,value in profit_list.items():
        if mmt_data[0] == key:
           context.bot.send_message(chat_id,value)

def add_dispatcher(dp):
    dp.add_handler(CommandHandler("mmt", mmt_command))
    dp.add_handler(CallbackQueryHandler(announce_mmt))
    return [BotCommand('mmt','/mmt 毛毛投股票代码 起始日期 结束日期')]
