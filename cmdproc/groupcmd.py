from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def group_cmd(update: Update, _:CallbackContext):
    print(update)
    chatId = update.message.chat_id
    print(chatId)
    member = update.message.from_user.full_name
    print(member)
    title = update.message.chat.title
    print(title)
    
    if chatId == -1001430794202 and title != None:
        update.message.reply_text(f"""
        Hello {member} Currently you are at Group {title}
        本队成员: a b c d""")

    else :
        update.message.reply_text(f"""
        Hello {member} Welcome to Group 
        学渣队： https://t.me/joinchat/h54IGoB7sHthN2Zl 群id: -1001430794202 
        渣学队： https://t.me/joinchat/Rcu2JXO8pAg1YTdl 群id: -1001478922081""")

def add_dispatcher(dp):
    dp.add_handler(CommandHandler("group", group_cmd))
    return []