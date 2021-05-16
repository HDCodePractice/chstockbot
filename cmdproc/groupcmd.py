from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def group_cmd(update: Update, callback: CallbackContext):
    chatId = update.message.chat_id
    print(chatId)
    member = update.message.from_user.full_name
    print(member)
    
    if chatId == -1001430794202 :
        update.message.reply_text("Hello""\nCurrently you are at Group""\n本队成员: a b c d")

    else :
        update.message.reply_text("Hello""\nWelcome to Group \" + \n学渣队： https://t.me/joinchat/h54IGoB7sHthN2Zl \n群id: -1001430794202 \n学霸队： https://t.me/joinchat/Rcu2JXO8pAg1YTdl   \n群id: -1001478922081")



def add_dispatcher(dp):
    dp.add_handler(CommandHandler("group", group_cmd))
    return []