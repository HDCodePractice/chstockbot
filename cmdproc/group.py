from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def echo(update: Update, _: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def ticker_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('学渣队： https://t.me/joinchat/h54IGoB7sHthN2Zl\n'
                              '渣学队： https://t.me/joinchat/Rcu2JXO8pAg1YTdl\n'
                              '学渣队 Bernie Veronica A Y Ben')

def add_dispatcher(dp):
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dp.add_handler(CommandHandler("group", ticker_command))
    return []