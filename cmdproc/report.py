from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


def report_cmd(update: Update, _:CallbackContext):
    fromuser = update.message.from_user.full_name
    print(fromuser)
    fromuserId = update.message.from_user.id
    print(fromuserId)
    forwardfrom = update.message.forward_from.full_name
    print(forwardfrom)
    forwardfromId = update.message.forward_from.id
    print(forwardfromId)
    message_forward_from = update.message.forward_from
    

    update.message.reply_text("name:" + fromuser + "id:" + fromuserId + "举报了 \n" 
                              "name:" + forwardfrom + "id:" + forwardfromId + "说了 \n"
                              + message_forward_from)


def add_dispatcher(dp):
    dp.add_handler(CommandHandler("r", report_cmd))
    return []