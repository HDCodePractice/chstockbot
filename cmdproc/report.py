from datetime import datetime
from os import error
from telegram import Update, ForceReply
import telegram
from telegram.error import BadRequest, TelegramError
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

admingroup = "-1001430794202"
groups =["-1001430794202","-512402539"]


def respose_txt(reporter, reportee, forward_message):
    msg = f"""
Name: {reporter.full_name} ID: {reporter.id}
Name: {reportee.full_name} ID: {reportee.id}
say: {forward_message}
    """
    return msg

def report_user(update: Update, callbackcontext:CallbackContext):
    incoming_message = update.message
    #verify if this is direct chat or forwarded chat
    print(incoming_message)
    if incoming_message.reply_to_message:
        #forward_msg = []
        reporter = incoming_message.from_user #举报人信息
        print("this message is quoted from another message")
        #grab user information based on chat type (group or private)
        reportee = incoming_message.reply_to_message.from_user #举报人信息
        
        #check if message is a text
        if incoming_message.reply_to_message.text:
            forward_message = incoming_message.reply_to_message.text
        else :
            forward_message = f"""not a message, but you can fetch it by searching message ID {incoming_message.reply_to_message.message_id}"""
        #send out message to chat
        incoming_message.reply_text(respose_txt(reporter,reportee, forward_message))

        #send direct message to admin group for audit
        incoming_message.bot.send_message(admingroup,respose_txt(reporter,reportee, forward_message))



    else :
        incoming_message.reply_text("没有发现被举报人的信息，请重新选择包含被举报人的信息并回复/r")
        print("this message doesnt contain reporter's name, please reply to the user's message you want to report")

    #temperary disable echo previous message expect text
   

def kick_member(update: Update, _:CallbackContext): #移除并拉黑举报人
    forwarding_message = update.message
    #check which command user sending
    command = forwarding_message.text
    #check if reply_to_message exist
    if forwarding_message.reply_to_message.text and "say:" in forwarding_message.reply_to_message.text :
        
        if "/kk" in command:
        #get reporter inforamtion
            member_info = forwarding_message.reply_to_message.text.split("\n")[0]
            member_id = member_info.split("ID: ")[-1]
        elif "/kr" in command:
            member_info = forwarding_message.reply_to_message.text.split("\n")[1]
            member_id = member_info.split("ID: ")[-1]
        else:
            forwarding_message.reply_text("no command found, please re-try")
        print(forwarding_message)
        #make sure the name and id being sent to admin group

        for group in groups:
            #kick reporter
            try:
                forwarding_message.bot.kick_chat_member(group,member_id)
                #在本地拉黑用户； 未来添加用户时需要检查blacklist文档确定该用户没有被拉黑
                f = open("blacklist.txt", "a")
                f.write("{member_id}/{group}\n".format(member_id,group))
                f.close()
                forwarding_message.reply_text(f"""已在群组{group}中删除并拉黑用户：{member_id}""")
            except Exception as e:
                forwarding_message.reply_text(f"""无法在群组{group}中删除用户：{member_id}; 请联系管理员删除, 详细信息如下：{e}""")
            #block reporter
        

    else:
        forwarding_message.reply_text(f"""没有发现被举报人的信息，请重新选择包含被举报人的信息并回复{command}""")    



def add_dispatcher(dp):
    dp.add_handler(CommandHandler("r", report_user))
    dp.add_handler(CommandHandler("kr", kick_member))
    dp.add_handler(CommandHandler("kk", kick_member))
    return []