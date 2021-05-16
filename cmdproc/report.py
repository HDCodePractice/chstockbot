from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


def respose_txt(reporter, reportee):
    msg = f"""
Name: {reporter.id} ID: {reporter.full_name}
Name: {reportee.id} ID: {reportee.full_name}
say:
    """
    return msg

def report_user(update: Update, _:CallbackContext):
    incoming_message = update.message
    #verify if this is direct chat or forwarded chat
    print(incoming_message)
    if incoming_message.reply_to_message:
        #forward_msg = []
        reporter = incoming_message.from_user #举报人信息
        print("this message is quoted from another message")
        #grab user information based on chat type (group or private)
        reportee = incoming_message.reply_to_message.from_user #举报人信息
        
        #send out message to chat
        incoming_message.reply_text(respose_txt(reporter,reportee))
        if incoming_message.reply_to_message.text is not None :
            forward_msg = incoming_message.reply_to_message.text
            incoming_message.reply_text(forward_msg)
        elif incoming_message.reply_to_message.animation is not None :
            forward_msg = incoming_message.reply_to_message.animation.file_id
            incoming_message.reply_animation(forward_msg)
        elif incoming_message.reply_to_message.audio is not None :
            forward_msg = incoming_message.reply_to_message.audio.file_id
            incoming_message.reply_audio(forward_msg)
        elif incoming_message.reply_to_message.sticker is not None :
            forward_msg =  incoming_message.reply_to_message.sticker.file_id
            incoming_message.reply_sticker(forward_msg)
        elif incoming_message.reply_to_message.video is not None :
            forward_msg =  incoming_message.reply_to_message.video.file_id
            incoming_message.reply_video(forward_msg)
        elif incoming_message.reply_to_message.voice is not None :
            forward_msg =  incoming_message.reply_to_message.voice.file_id
            incoming_message.reply_voice(forward_msg)
        elif incoming_message.reply_to_message.venue is not None :
            forward_msg =  incoming_message.reply_to_message.venue.file_id
            incoming_message.reply_venue(forward_msg) 
        elif incoming_message.reply_to_message.photo is not None :
            forward_msg =  incoming_message.reply_to_message.photo.copy
            incoming_message.reply_photo(forward_msg)    
        elif incoming_message.reply_to_message.poll is not None :
            forward_msg =  incoming_message.reply_to_message.poll.id
            incoming_message.reply_poll(forward_msg)
        elif incoming_message.reply_to_message.document is not None :
            forward_msg = incoming_message.reply_to_message.document.file_id
            incoming_message.reply_document(forward_msg)
        elif incoming_message.reply_to_message.text_html is not None :
            forward_msg = incoming_message.reply_to_message.text_html
            incoming_message.reply_html(forward_msg)           
        else:
            forward_msg = incoming_message.reply_to_message.text
            incoming_message.reply_text(forward_msg) 
    else :
        incoming_message.reply_text("没有发现被举报人的信息，请重新选择包含被举报人的信息并回复/r")
        print("this message doesnt contain reporter's name, please reply to the user's message you want to report")
def add_dispatcher(dp):
    dp.add_handler(CommandHandler("r", report_user))
    return []