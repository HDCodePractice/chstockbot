import os
from os import getenv
from dotenv import load_dotenv

if os.path.exists("local.env"):
    load_dotenv("local.env")

BOT_TOKEN = getenv("BOT_TOKEN")
API_ID = int(getenv("API_ID", "0"))
API_HASH = getenv("API_HASH")
SESSION_NAME = getenv("SESSION_NAME", "session")