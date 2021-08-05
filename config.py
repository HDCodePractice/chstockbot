#!/usr/bin/env python3

import json
import os
from dotenv import load_dotenv

loads = json.loads
load = json.load
dumps = json.dumps
dump = json.dump

run_path = os.path.split(os.path.realpath(__file__))[0]
config_path = run_path
config_file = ""

CONFIG = {}

def load_config():
    global CONFIG
    with open(config_file, 'r') as configfile:
        CONFIG = load( configfile )
    return CONFIG

def save_config():
    file_dir = os.path.split(config_file)[0]
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir)
    with open(config_file, 'w') as configfile:
        dump(CONFIG, configfile, indent=4,ensure_ascii=False)

def get_json():
    return dumps(CONFIG,indent=4,ensure_ascii=False)

def set_default():
    CONFIG.setdefault("Admin",[])       #管理员id
    CONFIG.setdefault("Admin_path","")  #Admin Shell Path
    save_config()

def get_admin_uids():
    if not CONFIG:
        load_config()
    return CONFIG.get("Admin", [])

if os.path.exists("local.env"):
    load_dotenv("local.env")

class ENV:
    WORKDIR=os.getcwd()
    # BotToken
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "") 
    # 是否为DEBUG模式（不发送消息，直接将消息打印到终端）
    DEBUG = eval(os.environ.get("DEBUG", "False"))
    # 发送夕阳红的代码和周期
    XYHTICKER = eval(os.environ.get("XYHTICKER", "[]"))
    # 发送目标CHATID
    XYHCHAT=os.environ.get("XYHCHAT", "")
    # 发送日志的CHATID
    XYHLOG=os.environ.get("XYHLOG", "")
    # 夕阳红数据源，可以选择 stooq 和 yahoo
    XYHSOURCE = os.environ.get("XYHSOURCE", "").split(" ")
    # 管理员列表，使用空格分隔
    ADMINS = os.environ.get("ADMINS", "").split(" ")
    # 管理群ChatID
    ADMIN_GROUP = os.environ.get("ADMIN_GROUP", "")
    # 管理的群和频道列表，使用空格分隔
    GROUPS = os.environ.get("GROUPS", "").split(" ")

if __name__ == "__main__":
    print(ENV.XYHTICKER)