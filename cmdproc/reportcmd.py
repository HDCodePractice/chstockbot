from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def report_cmd (update: Update, _: CallbackContext) -> None:
    member = update.message.from_user.full_name
    member_id = update.message.from_user.id
    if update.message.reply_to_message:
        report_message = update.message.reply_to_message.text
        report_member = update.message.reply_to_message.from_user.full_name
        report_member_id = update.message.reply_to_message.from_user.id
        bot_reply = f"""
Name: {member} User ID: {member_id} 举报了
Name: {report_member} User ID: {report_member_id} 说了:
{report_message}"""
        bot = update.effective_message.bot
        bot.send_message(-1001430794202,bot_reply)
    else:
        update.effective_message.reply_text("兄弟你需要回复一条消息举报")

def kick_cmd (update: Update, _: CallbackContext) -> None:
    bot = update.effective_message.bot
    bot.kick_chat_member(-1001409640737,"hi")

def add_dispatcher(dp):
    dp.add_handler(CommandHandler("r", report_cmd))
    dp.add_handler(CommandHandler("k", kick_cmd))
    return []

    