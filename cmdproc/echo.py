from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def echo(update: Update, _: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def ticker_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('GOEV')

def add_dispatcher(dp):
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dp.add_handler(CommandHandler("ticker", ticker_command))
    return []