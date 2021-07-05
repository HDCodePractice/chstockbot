from asyncio import sleep
from pyrogram import Client,filters
from pyrogram.types.messages_and_media.message import Message
from .. import config
from ..helpers.filters import command

@Client.on_message(command("s") & ~filters.edited)
async def song(_,message: Message):
    query = message.text.split(None, 1)
    if len(query) == 1:
        m = await message.reply_text("请使用 '/s 歌曲名' 来搜索歌曲")
        await sleep(5)
        await m.delete()
        await message.delete()
        return
    query = message.text.split(None, 1)[1]
    print(message)
    await message.reply_text(message.text)