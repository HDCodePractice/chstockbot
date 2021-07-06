import os
from os import getenv
from dotenv import load_dotenv

if os.path.exists("local.env"):
    load_dotenv("local.env")

BOT_TOKEN = getenv("BOT_TOKEN")
API_ID = int(getenv("API_ID", "0"))
API_HASH = getenv("API_HASH")
# userbot的session文件名前缀
SESSION_NAME = getenv("SESSION_NAME", "session")
ARQ_API_KEY = getenv("ARQ_API_KEY",None)
BOT_ID = ""
# bot username，识别命令@username
BOT_USERNAME = getenv("BOT_USERNAME","")
# 音乐长度（分钟）限制
DURATION_LIMIT = getenv("DURATION_LIMIT",60)