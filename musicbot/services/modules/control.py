from typing import Dict
from ..callsmusic import client

from pyrogram import Client,filters
from pyrogram.types.messages_and_media.message import Message

instances: Dict[int, Message] = {}

async def init_instances(chat_id):
    if chat_id not in instances:
        instances[chat_id] = None
        return
    if instances[chat_id]:
        await instances[chat_id].delete()
        instances[chat_id] = None

async def send_photo(chat_id,photo,caption=''):
    await init_instances(chat_id)
    mm = await client.send_photo(
        chat_id,
        photo,
        caption=caption)
    instances[chat_id] = mm

async def clean(chat_id):
    await init_instances(chat_id)