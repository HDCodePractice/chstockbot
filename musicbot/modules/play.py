from asyncio import sleep

from pyrogram import Client,filters
from pyrogram.types.messages_and_media.message import Message

from ..helpers.filters import command
from ..helpers.chat_id import get_chat_id

from ..services.callsmusic import callsmusic


@Client.on_message(command("join") & ~filters.edited)
async def start(_,message:Message):
    chat_id = get_chat_id(message.chat)
    await callsmusic.start(chat_id)
    await sleep(1)
    await message.delete()

@Client.on_message(command("leave") & ~filters.edited)
async def stop(_,message:Message):
    chat_id = get_chat_id(message.chat)
    await callsmusic.stop(chat_id)
    await sleep(1)
    await message.delete()

@Client.on_message(command("mute") & ~filters.edited)
async def mute(_,message:Message):
    chat_id = get_chat_id(message.chat)
    callsmusic.mute(chat_id)
    await sleep(1)
    await message.delete()
    
@Client.on_message(command("unmute") & ~filters.edited)
async def unmute(_,message:Message):
    chat_id = get_chat_id(message.chat)
    callsmusic.unmute(chat_id)
    await sleep(1)
    await message.delete()

@Client.on_message(command("pause") & ~filters.edited)
async def pause(_,message:Message):
    chat_id = get_chat_id(message.chat)
    callsmusic.pause(chat_id)
    await sleep(1)
    await message.delete()

@Client.on_message(command("play") & ~filters.edited)
async def play(_,message:Message):
    chat_id = get_chat_id(message.chat)
    playing = callsmusic.resume(chat_id)
    if not playing:
        mm = await message.reply_text("XD现在没有可以播放的了，用 `/s 歌曲` 来搜索个想听的吧～")
        await sleep(5)
        await mm.delete()
    await sleep(1)
    await message.delete()