from pyrogram import Client,filters
from .. import config

@Client.on_message(filters.command(["s",f"s@{config.BOT_USERNAME}"]))
async def song(clent,message):
    print(message)
    await message.reply_text(message.text)