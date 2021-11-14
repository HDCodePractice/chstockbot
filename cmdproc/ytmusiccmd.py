import os,asyncio
from telegram import Update,  BotCommand,ParseMode
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from json import dumps
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
import datetime,os,config
from bot import sendmsg
from config import ENV
from util.youtube import download_youtube,YoutubeDLError,get_info,init_yt
from util.tgutil import get_user_link, delay_del_msg, get_group_info

admingroup = ENV.ADMIN_GROUP
groups = ENV.GROUPS
admins = ENV.ADMINS
debug= ENV.DEBUG

pic = "https://c.tenor.com/XasjKGMk_wAAAAAC/load-loading.gif" #需要被转成ENV变量


def ytmusic_command(update: Update, context: CallbackContext):
    alert_message = "输入格式不对，请使用 /y url这样的格式查询"
    incoming_message = update.effective_message
    chat_id = update.effective_chat.id
    user = update.effective_user
    if len(incoming_message.text.split(' ')) <= 1:
        incoming_message.reply_text(alert_message)
        return
    url_link = incoming_message.text.split(' ')[-1]
    try:
        info = get_info(url_link)
        if info == None:
            incoming_message.reply_text(f"哥们儿您输入的网址好像不存在啊，请重新输入")
            return
        inform_msg=incoming_message.reply_text(f"正在为您下载音乐 大小:{info['filesize']/1024/1024:.2f}MB 预估:{info['waiting_time']:.2f}秒 请耐心等待 点播者：{user.full_name}")
        download_gif=incoming_message.reply_animation(pic)
        status,output = download_youtube(url_link)
        if status == False:
            reply_msg=f"亲爱的{user.full_name}，bot出错啦，请稍后再试" if output == None else f"亲爱的{user.full_name}，{output}"
            incoming_message.reply_text(reply_msg)
            return
        if status == True:
            download_file = f"assets/{info['id']}.{info['ext']}"
            incoming_message.bot.delete_message(inform_msg.chat_id,inform_msg.message_id)
            incoming_message.bot.delete_message(download_gif.chat_id,download_gif.message_id)
            finish_notify_msg=incoming_message.reply_text(f"已从Youtube下载完成 正在上传中 请耐心等待 点播者：{user.full_name}")
            incoming_message.bot.edit_message_text(chat_id=finish_notify_msg.chat_id,message_id=finish_notify_msg.message_id,text=f"{info['title']}  点播者：{user.full_name}")
            incoming_message.reply_html(info['thumbnail'])
            incoming_message.reply_audio(open(download_file, 'rb'))
            
    except Exception as err:
        sendmsg(context.bot,admingroup,f"下载音乐文件报错了，具体信息是{err}",debug)
        #context.bot.send_message(chat_id=admingroup,text=f"下载音乐文件报错了，具体信息是{err}")

def add_dispatcher(dp):
    dp.add_handler(CommandHandler("y", ytmusic_command))
    return [BotCommand('y','/y youtube音乐链接')]
