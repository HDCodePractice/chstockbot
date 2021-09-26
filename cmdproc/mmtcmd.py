from telegram import Update,  BotCommand
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from json import dumps
from stockutil.ticker import Ticker
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
import datetime
from config import ENV
from util.tgutil import delay_del_msg

admingroup = ENV.ADMIN_GROUP
groups = ENV.GROUPS
admins = ENV.ADMINS

ten_year_date = datetime.datetime.today().date() - datetime.timedelta(days=3650)
one_year_date = datetime.datetime.today().date() - datetime.timedelta(days=365)
def mmt_command(update: Update, context: CallbackContext) -> None:
    mmt_starttime = datetime.datetime.today().date() - datetime.timedelta(days=365)
    mmt_endtime = datetime.datetime.today().date()
    incoming_message = update.effective_message
    user = incoming_message.from_user.username
    err_msg = "格式错误啦， 请输入/mmt 股票代码 起始日期(可选) 结束时间(可选) (日期格式：yyyymmdd)\n"
    msg_l = incoming_message.text.split(" ")
    if len(msg_l) == 1 or len(msg_l) > 4:
        update.message.reply_text(err_msg)        
        return
    try:  
        sy,sm,sd = msg_l[2][:4],msg_l[2][-4:-2],msg_l[2][-2:]        
        mmt_starttime = datetime.date(int(sy),int(sm),int(sd))
        ey,em,ed = msg_l[3][:4],msg_l[3][-4:-2],msg_l[3][-2:]
        mmt_endtime = datetime.date(int(ey),int(em),int(ed))
    except ValueError:
        update.message.reply_text(err_msg)
        return    
    except IndexError:
        update.message.reply_text(f"由于未检测到或只检测到部分日期参数，毛毛投即将使用的日期参数为:{mmt_starttime}/{mmt_endtime}\n")
    except Exception:
        update.message.reply_text(err_msg)
        return
    #准备返回3个按钮
    keyboard = [[
        InlineKeyboardButton(text=f"{mmt_starttime}", callback_data=f"{msg_l[1].lower()}:{mmt_starttime}:{mmt_endtime}:{user}"),
        InlineKeyboardButton(text=f"过去一年", callback_data=f"{msg_l[1].lower()}:{one_year_date}:{mmt_endtime}:{user}"),
        InlineKeyboardButton(text=f"过去10年", callback_data=f"{msg_l[1].lower()}:{ten_year_date}:{mmt_endtime}:{user}")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg_text = f"股票代码：{msg_l[1].lower()}\n请选择想要进行毛毛投利润率计算的日期：\n"
    update.message.reply_markdown_v2(msg_text,reply_markup=reply_markup)


def announce_mmt(update: Update, context:CallbackContext):
    #获取点击按钮的用户信息和毛毛投信息
    reply_user_id = update.effective_chat.username
    reply_user_name = update.effective_chat.full_name
    mmt_data = update.callback_query.data.split(":")
    chat_id = update.effective_chat.id
    reply_message = ""
    #如果不是提问人的id， 回复信息
    alert_msg = f"亲爱的{reply_user_name}, 这个不是你提的问题，请不要随意点击！如果想要查询毛毛投的信息，请自己输入命令！\n"
    if reply_user_id != mmt_data[3]:
        update.callback_query.bot.send_message(chat_id,alert_msg)
        return
    #尝试计算毛毛投利润率
    try:      
        t = Ticker(mmt_data[0], "web","stooq",starttime= mmt_data[1], endtime=mmt_data[2])
        t.load_data(updateEndtime=True)
        if str(t.starttime) != str(mmt_data[1]):
            reply_message += f"由于起始日期{mmt_data[1]}的数据不存在，自动转为最近的有数据的日期:{t.starttime}\n"
        if str(t.endtime) != str(mmt_data[2]):
            reply_message += f"由于结束日期{mmt_data[2]}的数据不存在，自动转为最近的有数据的日期:{t.endtime}\n"
        t.cal_profit()
        reply_message += t.gen_mmt_msg()
        update.callback_query.bot.send_message(chat_id,reply_message)
    except Exception as err:
        update.callback_query.bot.send_message(chat_id,"数据正在更新中；请稍后再试\n")
        #update.message.bot.send_message(admingroup, f"毛毛投数据出错了！具体错误为：{err}")


def add_dispatcher(dp):
    dp.add_handler(CommandHandler("mmt", mmt_command))
    dp.add_handler(CallbackQueryHandler(announce_mmt))
    return [BotCommand('mmt','/mmt 毛毛投股票代码 起始日期 结束日期')]
