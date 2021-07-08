from pyrogram import Client

from musicbot import config

client = Client(config.SESSION_NAME, config.API_ID, config.API_HASH,plugins={"root":"musicbot.service.modules"})
run = client.run
