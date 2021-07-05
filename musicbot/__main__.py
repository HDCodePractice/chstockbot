from pyrogram import Client as Bot

from musicbot.config import API_HASH
from musicbot.config import API_ID
from musicbot.config import BOT_TOKEN
from musicbot.services import run

bot = Bot(
    ':memory:',
    API_ID,
    API_HASH,
    bot_token=BOT_TOKEN,
    plugins={'root': 'musicbot.modules'},
)
bot.start()
run()
