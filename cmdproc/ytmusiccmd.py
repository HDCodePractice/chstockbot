import os,asyncio
from telegram import Update,  BotCommand,ParseMode
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from json import dumps
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
import datetime,os,config
from bot import sendmsg
from config import ENV
from util.youtube import download_youtube,YoutubeDLError
from util.tgutil import get_user_link, delay_del_msg, get_group_info

admingroup = ENV.ADMIN_GROUP
groups = ENV.GROUPS
admins = ENV.ADMINS
debug= ENV.DEBUG

def ytmusic_command(update: Update, context: CallbackContext):
    alert_message = "输入格式不对，请使用 /y url这样的格式查询"
    incoming_message = update.effective_message
    user = update.effective_user
    if len(incoming_message.text.split(' ')) <= 1:
        incoming_message.reply_text(alert_message)
        return
    url_link = incoming_message.text.split(' ')[-1]
    try:
        incoming_message.reply_text(f"亲爱的{user.full_name}，正在为您下载音乐，请稍等")
        status,output = download_youtube(url_link)
        if status == False:
            reply_msg=f"亲爱的{user.full_name}，bot出错啦，请稍后再试" if output == None else f"亲爱的{user.full_name}，{output}"
            incoming_message.reply_text(reply_msg)
            return
        if status == True:
            incoming_message.reply_audio(open(os.path.expanduser(output), 'rb'))
            
    except Exception as err:
        sendmsg(context.bot,admingroup,f"下载音乐文件报错了，具体信息是{err}",debug)
        #context.bot.send_message(chat_id=admingroup,text=f"下载音乐文件报错了，具体信息是{err}")

def add_dispatcher(dp):
    dp.add_handler(CommandHandler("y", ytmusic_command))
    return [BotCommand('y','/y youtube音乐链接')]
