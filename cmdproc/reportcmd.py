from telegram import Update, ForceReply, BotCommand
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


def report_command(update: Update, context:CallbackContext) -> None:
    print(update)
    reporter = update.message.from_user.full_name
    print(reporter)
    reporterId = update.message.from_user.id
    print(reporterId)
    scammer = update.message.reply_to_message.from_user.full_name
    print(scammer)
    scammerId = update.message.reply_to_message.from_user.id
    print(scammerId)
    message_reply = update.message.reply_to_message.text
    

    update.message.reply_text(f"""
name: {reporter} id: {reporterId} 举报了~ 
name: {scammer} id: {scammerId}说了 
{message_reply}""")


def add_dispatcher(dp):
    dp.add_handler(CommandHandler("r", report_command))
    return [BotCommand('r','举报一个对话')]