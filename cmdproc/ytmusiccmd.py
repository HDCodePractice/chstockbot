import asyncio
import datetime
import os
from json import dumps

import config
from bot import sendmsg
from config import ENV
from telegram import BotCommand, ParseMode, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from util.tgutil import delay_del_msg, get_group_info, get_user_link
from util.youtube import YoutubeDLError, download_youtube, get_info, search

admingroup = ENV.ADMIN_GROUP
groups = ENV.GROUPS
admins = ENV.ADMINS
debug = ENV.DEBUG

pic = "https://c.tenor.com/XasjKGMk_wAAAAAC/load-loading.gif"  # 需要被转成ENV变量


def ytmusic_command(update: Update, context: CallbackContext):
    alert_message = "输入格式不对，请使用 /y 音乐名 这样的格式查询"
    incoming_message = update.effective_message
    user = update.effective_user
    if len(incoming_message.text.split(' ')) <= 1:
        incoming_message.reply_text(alert_message)
        return
    url_link = search(incoming_message.text.split(' ')[-1])
    info = get_info(url_link)
    if info == None:
        incoming_message.reply_text(f"哥们儿您输入的网址好像不存在啊，请重新输入")
        return
    download_gif = incoming_message.reply_animation(
        pic, caption=f"正在为您下载音乐 大小:{info['filesize']/1024/1024:.2f}MB 预估:{info['waiting_time']:.2f}秒 请耐心等待 点播者：{user.full_name}")
    status, output = download_youtube(url_link, '/tmp')
    if status == False:
        reply_msg = f"亲爱的{user.full_name}，bot出错啦，请稍后再试" if output == None else f"亲爱的{user.full_name}，{output}"
        incoming_message.reply_text(reply_msg)
    if status == True:
        download_file = output
        download_gif.edit_caption(
            caption=f"已从Youtube下载完成 正在上传中 请耐心等待 点播者：{user.full_name}")
        incoming_message.reply_audio(open(download_file, 'rb'), thumb=info["thumbnails"][0]["url"].split(
            "?")[0], caption=f"{info['title']}  点播者：{user.full_name}")
    download_gif.delete()


def add_dispatcher(dp):
    dp.add_handler(CommandHandler("y", ytmusic_command))
    return [BotCommand('y', '/y youtube音乐链接')]
