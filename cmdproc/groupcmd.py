from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def group_command(update: Update, _: CallbackContext) -> None:
    if update.effective_chat.id == -1001478922081:
       update.message.reply_text("our group contains " + format(update.message.chat.get_members_count()) + """ members
本组成员: 张富贵, Joe Shen, Stephen.""")
    else:
       update.message.reply_text(
"""学渣队： https://t.me/joinchat/h54IGoB7sHthN2Zl
渣学队： https://t.me/joinchat/Rcu2JXO8pAg1YTdl
        """)

def add_dispatcher(dp):
    dp.add_handler(CommandHandler("group", group_command))
    return []