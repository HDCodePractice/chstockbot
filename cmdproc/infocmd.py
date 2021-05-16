from telegram import Update, ForceReply
from telegram import botcommand
from json import dumps

def ticker_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('GOEV')

def add_dispatcher(dp):
    dp.add_handler(CommandHandler("info", info_command))
    return []