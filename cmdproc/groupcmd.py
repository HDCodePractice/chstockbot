from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def groupcmd(update: Update, _: CallbackContext) -> None:
    if update.message.chat.id == -1001478922081:
        # update.effective_chat.id == -1001478922081:  一样的效果
        update.message.reply_text("张富贵,Joe Shen,Stephen")
    else:
        update.message.reply_text("学渣队： https://t.me/joinchat/h54IGoB7sHthN2Zl  id: -1001430794202; 渣学队： https://t.me/joinchat/Rcu2JXO8pAg1YTdl  id: -1001478922081")

def add_dispatcher(dp):
    dp.add_handler(CommandHandler("group", groupcmd))
    return []


