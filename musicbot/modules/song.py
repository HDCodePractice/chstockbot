from pyrogram import Client,filters
from .. import config
from ..helpers.filters import command

@Client.on_message(command("s"))
async def song(clent,message):
    print(message)
    await message.reply_text(message.text)