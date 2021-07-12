from pyrogram import Client as Bot

from musicbot.config import API_HASH
from musicbot.config import API_ID
from musicbot.config import BOT_TOKEN
from musicbot.config import BOT_ID
from musicbot.config import BOT_USERNAME
from musicbot.services.callsmusic import run
from musicbot import config
bot = Bot(
    ':memory:',
    API_ID,
    API_HASH,
    bot_token=BOT_TOKEN,
    plugins={'root': 'musicbot.modules'},
)
client = bot.start()
BOT_ID = client.get_me().id
if not BOT_USERNAME == bot.get_me()["username"]:
    username = bot.get_me()["username"]
    print(f"config.json username must change to { username }")
    bot.stop()
else:
    from musicbot.modules import control
    control.bot = client
    print(f"Starting Bot... ID: {BOT_ID} , Username: {BOT_USERNAME}")
    run()
