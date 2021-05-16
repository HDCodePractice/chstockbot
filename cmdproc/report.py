from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


def respose_txt(reporter_name, reporter_id, reportee_name,reportee_id):
    msg = "name: {reporterName} ID: {reporterId} 举报了 \nname: {reporteeName} ID: {reporteeId} \n说了: \n".format(reporterName = reporter_name, reporterId = reporter_id, reporteeName = reportee_name, reporteeId = reportee_id)
    return msg

def report_user(update: Update, _:CallbackContext):
    incoming_message = update.message
    #verify if this is direct chat or forwarded chat
    print(incoming_message)
    if incoming_message.reply_to_message is not None :
        #forward_msg = []
        reporter = incoming_message.chat.get_member(incoming_message.from_user.id) #举报人信息
        if reporter["user"]["last_name"] is not None and reporter["user"]["first_name"] is not None :
            reporter_name = reporter["user"]["first_name"] + " " + reporter["user"]["last_name"] 
        elif reporter["user"]["last_name"] is not None and reporter["user"]["first_name"] is None :
            reporter_name = reporter["user"]["last_name"] 
        elif reporter["user"]["last_name"] is None and reporter["user"]["first_name"] is not None :
            reporter_name = reporter["user"]["first_name"]
        else :
            reporter_name = "unknown user"
        #获得转发信息


        #forward_msg = update.effective_message
        print("this message is quoted from another message")
        #grab user information based on chat type (group or private)
        if incoming_message.chat.type == None :
            print("this is private chat")
            reportee = incoming_message.reply_to_message.chat.get_member(incoming_message.reply_to_message.chat.id) #被举报人信息
            if reportee["user"]["last_name"] is not None and reportee["user"]["first_name"] is not None :
                reportee_name = reportee["user"]["first_name"] + " " + reportee["user"]["last_name"] 
            elif reportee["user"]["last_name"] is not None and reportee["user"]["first_name"] is None :
                reportee_name = reportee["user"]["last_name"] 
            elif reportee["user"]["last_name"] is None and reportee["user"]["first_name"] is not None :
                reportee_name = reportee["user"]["first_name"]
            else :
                reportee_name = "unknown user"
            
        else :
            print("this is group chat")
            reportee = incoming_message.reply_to_message.chat.get_member(incoming_message.reply_to_message.from_user.id) #被举报人信息
            if reportee["user"]["last_name"] is not None and reportee["user"]["first_name"] is not None :
                reportee_name = reportee["user"]["first_name"] + " " + reportee["user"]["last_name"] 
            elif reportee["user"]["last_name"] is not None and reportee["user"]["first_name"] is None :
                reportee_name = reportee["user"]["last_name"] 
            elif reportee["user"]["last_name"] is None and reportee["user"]["first_name"] is not None :
                reportee_name = reportee["user"]["first_name"]
            else :
                reportee_name = "unknown user"
        #send out message to chat

        if incoming_message.reply_to_message.text is not None :
            forward_msg = incoming_message.reply_to_message.text
            incoming_message.reply_text(respose_txt(reporter_name, reporter["user"]["id"], reportee_name, reportee["user"]["id"]) + forward_msg)
        elif incoming_message.reply_to_message.animation is not None :
            forward_msg = incoming_message.reply_to_message.animation.file_id
            incoming_message.reply_text(respose_txt(reporter_name, reporter["user"]["id"], reportee_name, reportee["user"]["id"]))
            incoming_message.reply_animation(forward_msg,allow_sending_without_reply=True)
        elif incoming_message.reply_to_message.audio is not None :
            forward_msg = incoming_message.reply_to_message.audio.file_id
            incoming_message.reply_text(respose_txt(reporter_name, reporter["user"]["id"], reportee_name, reportee["user"]["id"]))
            incoming_message.reply_audio(forward_msg,allow_sending_without_reply=True)
        elif incoming_message.reply_to_message.sticker is not None :
            forward_msg =  incoming_message.reply_to_message.sticker.file_id
            incoming_message.reply_text(respose_txt(reporter_name, reporter["user"]["id"], reportee_name, reportee["user"]["id"]))
            incoming_message.reply_sticker(forward_msg,allow_sending_without_reply=True)
        elif incoming_message.reply_to_message.document is not None :
            forward_msg = incoming_message.reply_to_message.document.file_id
            incoming_message.reply_text(respose_txt(reporter_name, reporter["user"]["id"], reportee_name, reportee["user"]["id"]))
            incoming_message.reply_document(forward_msg,allow_sending_without_reply=True)         
            #incoming_message.reply_text(respose_txt(reporter_name, reporter["user"]["id"], reportee_name, reportee["user"]["id"]))
            
    else :
        incoming_message.reply_text("没有发现被举报人的信息，请重新选择包含被举报人的信息并回复/r")
        print("this message doesnt contain reporter's name, please reply to the user's message you want to report")
def add_dispatcher(dp):
    dp.add_handler(CommandHandler("r", report_user))
    return []