from pyrogram import Client as Bot

from .config import API_HASH
from .config import API_ID
from .config import BOT_TOKEN
from .config import BOT_ID
from .config import BOT_USERNAME
from musicbot.services import run

bot = Bot(
    ':memory:',
    API_ID,
    API_HASH,
    bot_token=BOT_TOKEN,
    plugins={'root': 'musicbot.modules'},
)
bot.start()
if not BOT_USERNAME == bot.get_me()["username"]:
    username = bot.get_me()["username"]
    print(f"config.json username must change to { username }")
    bot.stop()
else:
    print(f"Starting Bot... ID: {BOT_ID} , Username: {BOT_USERNAME}")
    run()
