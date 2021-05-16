from telegram import Update, ForceReply, User
import telegram
from telegram.botcommand import BotCommand
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def report_cmd(update: Update, _: CallbackContext) -> None:
    #reporter info 
    reporterName = update.message.from_user
    reporterId = update.message.from_user.id
    #spammer info 
    spammerName = update.message.reply_to_message.from_user.full_name
    spammerId = update.message.reply_to_message.from_user.id
    spammerContent = update.message.reply_to_message.text
    update.message.reply_text('''
    "Member:" + reporterName +"ID:" + str(reporterId) + "举报了"
    + "Member:"+ spamerName + "ID:" + str(spammerId) +"说了："
    + spammerContente
    ''')


def add_dispatcher(dp):
    dp.add_handler(CommandHandler("r", report_cmd))
    return [BotCommand('r','举报一个对话')]


