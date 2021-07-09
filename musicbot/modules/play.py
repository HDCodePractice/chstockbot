from asyncio import sleep

from pyrogram import Client,filters
from pyrogram.types.messages_and_media.message import Message

from ..helpers.filters import command
from ..helpers.chat_id import get_chat_id

from ..services.callsmusic import callsmusic
from ..services.queues import queues


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

@Client.on_message(command("volume") & ~filters.edited)
async def volume(_,message:Message):
    if len(message.command) < 2:
        mm = await message.reply("请告诉我音量(0-200)值")
    else:
        chat_id = get_chat_id(message.chat)
        await callsmusic.volume(chat_id,message.command[1])
    await sleep(5)
    if mm : 
        await mm.delete()
    await message.delete()

@Client.on_message(command("skip") & ~filters.edited)
async def skip(_,message:Message):
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.active_chats:
        mm = await message.reply_text("快去用 `/s 歌曲` 点个歌再考虑是不是要跳过好不好")
        await sleep(5)
        await mm.delete()
    else:
        await callsmusic.skip(chat_id)
    await message.delete()


@Client.on_message(command("s") & ~filters.edited)
async def state(_,message:Message):
    chat_id = get_chat_id(message.chat)
    try:
        print("instances:\n",callsmusic.instances,"\n")
        print("queue:\n",queues.getlist(chat_id),"\n")
        print("active_chats",callsmusic.active_chats,"\n")
        print("inputfile:\n",callsmusic.instances[chat_id].input_filename,"\n")
    except Exception as e:
        print(e)
    await message.delete()