from typing import BinaryIO, Dict, Union
from ..callsmusic import client

from pyrogram import types
from pyrogram import Client,filters
from pyrogram.types.messages_and_media.message import Message

instances: Dict[int, Message] = {}

async def init_instance(chat_id):
    if chat_id not in instances:
        instances[chat_id] = None
        return
    if instances[chat_id]:
        await instances[chat_id].delete()
        instances[chat_id] = None

async def send_playing(chat_id: Union[int,str],song:Dict):
    await init_instance(chat_id)
    mm = await client.send_photo(
        chat_id,
        song['thumbnail'],
        caption=f"正在播放 {song['user'].first_name} 点播的\n`{song['title']}` 来自于 `{song['singers']}` 时长 {song['sduration']}"
    )
    instances[chat_id] = mm

async def clean(chat_id):
    await init_instance(chat_id)