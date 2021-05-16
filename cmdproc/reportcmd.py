from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def report_cmd (update: Update, _: CallbackContext) -> None:
    member = update.message.from_user.full_name
    member_id = update.message.from_user.id
    report_message = update.message.reply_to_message.text
    report_member = update.message.reply_to_message.from_user.full_name
    report_member_id = update.message.reply_to_message.from_user.id
    update.message.reply_text("Name: " + member + " User ID: " + str(member_id) + " 举报了" + "\nName: " + report_member + " User ID: " + str(report_member_id) + " 说了: " + "\n" + report_message)

def add_dispatcher(dp):
    dp.add_handler(CommandHandler("r", report_cmd))
    return []

    