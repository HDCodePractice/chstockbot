from telegram import Update, ForceReply, BotCommand
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from json import dumps

def info_command(update: Update, context:CallbackContext) -> None:
    u = str(update)
    u = dumps(eval(u),indent=2)
    update.message.reply_text(u)

def add_dispatcher(dp):
    dp.add_handler(CommandHandler("info", info_command))
    return []