from email.message import Message
from typing import List

import requests
from config import ENV
from telegram import (BotCommand, InlineKeyboardButton, InlineKeyboardMarkup,
                      Message, Update)
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler
from telegram.utils.helpers import escape_markdown
from util.youtube import download_youtube, get_info, search

pic = "https://c.tenor.com/XasjKGMk_wAAAAAC/load-loading.gif"  # 需要被转成ENV变量

kb = [[InlineKeyboardButton("删除歌曲", callback_data="ytmusic_delete:")]]


def delete_reply_msg(context: CallbackContext):
    msgs = context.job.context
    for msg in msgs:
        context.bot.delete_message(msg.chat.id, msg.message_id)


def set_delay_delete(context, msgs: List[Message], delay: int = 10):
    # 设置延迟删除消息
    delete_time = delay
    job = context.job_queue.run_once(
        delete_reply_msg, delete_time, context=msgs, name=f"delete_msg_{msgs[0].message_id}")


def delete_music(update: Update, context: CallbackContext):
    querydata = update.callback_query.data.split(':')
    org_uid = querydata[1]
    uid = str(update.effective_user.id)
    if org_uid != uid and uid not in ENV.MUSIC_ADMINS:
        update.callback_query.answer(
            text="您不是管理员，这首音乐也不是您点播的，您可以点右键在自己的存储里删除这首音乐，如果您觉得这首歌不值得推荐给大家听，直接点👎就好，管理员会清除它的",
            show_alert=True)
        return
    update.effective_message.delete()


def ytmusic_command(update: Update, context: CallbackContext):
    if str(update.effective_chat.id) not in ENV.MUSIC_GROUP:
        return
    alert_message = "输入格式不对，请使用 /y 音乐名 这样的格式查询"
    incoming_message = update.effective_message
    user = update.effective_user
    user_info = f"[{user.full_name}](tg://user?id={user.id})"
    if len(incoming_message.text.split(' ')) <= 1:
        msg = incoming_message.reply_text(alert_message)
        set_delay_delete(context, [msg, incoming_message])
        return
    url_link = search(' '.join(context.args))
    info = get_info(url_link)
    if info == None:
        msg = incoming_message.reply_text(f"哥们儿您输入的网址好像不存在啊，请重新输入")
        set_delay_delete(context, [msg, incoming_message])
        return
    if info["filesize"] > 20971520:  # 判断文件大小
        size = int(info["filesize"]/1024/1024)
        err_msg = f"您要下载的音乐竟然有{size}MB之大，这是要撑爆Telegram的节奏啊！"
        msg = incoming_message.reply_text(err_msg)
        set_delay_delete(context, [msg, incoming_message])
        return
    download_gif = incoming_message.reply_animation(
        pic, caption=f"正在为您下载音乐 大小:{info['filesize']/1024/1024:.2f}MB 请耐心等待 点播者：{user.full_name}")
    status, output = download_youtube(url_link, f"{ENV.MUSIC_CACHE}")
    if status == False:
        reply_msg = f"亲爱的{user.full_name}，bot出错啦，请稍后再试" if output == None else f"亲爱的{user.full_name}，{output}"
        incoming_message.reply_text(reply_msg)
    if status == True:
        download_file = output
        download_gif.edit_caption(
            caption=f"已从Youtube下载完成 正在上传中 请耐心等待 点播者：{user.full_name}")
        img_url = info["thumbnails"][0]["url"]
        img_data = requests.get(img_url).content
        uid = user.id
        kb[0][0].callback_data = f"ytmusic_delete:{uid}"
        incoming_message.reply_audio(
            open(download_file, 'rb'),
            thumb=img_data,
            caption=f"{escape_markdown(info['title'],version=2)}\n点播者：{user_info}",
            quote=False,
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="MarkdownV2")
    download_gif.delete()
    incoming_message.delete()


def add_dispatcher(dp):
    dp.add_handler(CommandHandler("y", ytmusic_command))
    dp.add_handler(CallbackQueryHandler(
        delete_music, pattern="^ytmusic_delete:[A-Za-z0-9_-]*"))
    return [BotCommand('y', '/y youtube音乐链接')]
