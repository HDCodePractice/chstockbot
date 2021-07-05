from asyncio import sleep
from pyrogram import Client,filters
from pyrogram.types.messages_and_media.message import Message
from pyrogram.types import InputMediaPhoto
from .. import config
from ..helpers.filters import command
from ..helpers.chat_id import get_chat_id
from Python_ARQ import ARQ
from aiohttp import ClientSession
from ..helpers.funcs import *
from ..services import queues


# 初始化ARQ API
session = ClientSession()
arq = ARQ("https://thearq.tech",config.ARQ_API_KEY,session)

@Client.on_message(command("s") & ~filters.edited)
async def song(_,message: Message):
    query = message.text.split(None, 1)
    if len(query) == 1:
        m = await message.reply_text("请使用 '/s 歌曲名' 来搜索歌曲")
        await sleep(5)
        await m.delete()
        await message.delete()
        return
    query = query[1]
    if message.sender_chat:
        message.from_user = message.sender_chat
        message.from_user.first_name = message.sender_chat.username
    m = await message.reply_text(f"在油管上疯狂搜索 `{query}` 中")
    res = await arq.youtube(query)
    if not res.ok:
        await m.edit("嘛都木有找到... 要不考虑再试试别的？...")
        await sleep(5)
        await m.delete()
        await message.delete()
        return
    results= res.result
    slink= f"https://youtube.com{results[0]['url_suffix']}"
    title = results[0]["title"]
    singers = results[0]["channel"]
    thumbnail = results[0]["thumbnails"][0]
    sduration = results[0]["duration"]
    duration= time_to_seconds(sduration)
    views = results[0]["views"]
    if int(duration)>=1800: #duration limit
            await m.edit("兄弟，实在太太太长了，已经超过了30分钟鸟~")
            await sleep(5)
            await m.delete()
            await message.delete()
            return
    chat_id = get_chat_id(message.chat)
    await m.delete()
    m = await message.reply_photo(thumbnail,caption=f"{title} {sduration} {views}")
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    position = await queues.put(
        chat_id,slink=slink,
        title=title,singers=singers,
        thumbnail=thumbnail,sduration=sduration,
        views=views)
    await sleep(15)
    await m.delete()
    await message.delete()