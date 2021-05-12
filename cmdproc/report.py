from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


def respose_txt(reporter_name, reporter_id, reportee_name,reportee_id, forward_msg):
    msg = "name: {reporterName} ID: {reporterId} 举报了 \nname: {reporteeName} ID: {reporteeId} \n说了: {forwardMsg}".format(reporterName = reporter_name, reporterId = reporter_id, reporteeName = reportee_name, reporteeId = reportee_id, forwardMsg = forward_msg)
    return msg

def report_user(update: Update, _:CallbackContext):
    incoming_message = update.message
    #verify if this is direct chat or forwarded chat
    print(incoming_message)
    if incoming_message.reply_to_message is not None :
        reporter = incoming_message.chat.get_member(incoming_message.from_user.id) #举报人信息
        reporter_name = reporter["user"]["first_name"] + " " + reporter["user"]["last_name"] if reporter["user"]["is_bot"] == False else reporter["user"]["first_name"]
        forward_msg = str(incoming_message.reply_to_message.text)
        #grab user information based on chat type (group or private)
        if incoming_message.chat.type == None :
            print("this is private chat")
            reportee = incoming_message.reply_to_message.chat.get_member(incoming_message.reply_to_message.chat.id) #被举报人信息
            reportee_name = reportee["user"]["first_name"] + " " + reportee["user"]["last_name"] if reportee["user"]["is_bot"] == False else reportee["user"]["first_name"]
            print("this message is quoted from another message")
        else :
            print("this is group chat")
            reportee = incoming_message.reply_to_message.chat.get_member(incoming_message.reply_to_message.from_user.id) #被举报人信息
            reportee_name = reportee["user"]["first_name"] + " " + reportee["user"]["last_name"] if reportee["user"]["is_bot"] == False else reportee["user"]["first_name"]
            print("this message is quoted from another message")
        #send out message to chat
        incoming_message.reply_text(respose_txt(reporter_name, reporter["user"]["id"], reportee_name, reportee["user"]["id"], forward_msg))
            
    else :
        incoming_message.reply_text("没有发现被举报人的信息，请重新选择包含被举报人的信息并回复/r")
        print("this message doesnt contain reporter's name, please reply to the user's message you want to report")
def add_dispatcher(dp):
    dp.add_handler(CommandHandler("r", report_user))
    return []