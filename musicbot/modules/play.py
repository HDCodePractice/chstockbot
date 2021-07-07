from pyrogram import Client,filters
from pyrogram.types.messages_and_media.message import Message

from ..helpers.filters import command
from ..helpers.chat_id import get_chat_id

from ..services.callsmusic import callsmusic


@Client.on_message(command("join") & ~filters.edited)
async def start(_,message:Message):
    chat_id = get_chat_id(message.chat)
    await callsmusic.start(chat_id)

@Client.on_message(command("leave") & ~filters.edited)
async def stop(_,message:Message):
    chat_id = get_chat_id(message.chat)
    await callsmusic.stop(chat_id)