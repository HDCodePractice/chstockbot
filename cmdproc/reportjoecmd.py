from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

vio_text = "举报信息"

def report_command(update: Update, _: CallbackContext) -> None:
    print(update)
    #update._ffective_chat
    message = update.effective_message
    user = message.from_user
    reply_user = message.reply_to_message.from_user
    if message.reply_to_message != None:     #检查举报命令是否为回复信息
        if message.reply_to_message.text == None:    #检查被举报的信息内容是否为文本信息
            vio_text = "非文本信息" #若被举报信息不含文本则定义举报内容为非文本信息                         
        else:                
            vio_text = message.reply_to_message.text #赋值被举报信息
            bot_reply = f"""
User 用户: {user.full_name}  ID: {user.id} Reported 举报了
User 用户: {reply_user.full_name} ID: {reply_user.id}
Reported Content 被举报内容:
{vio_text}
"""


            #bot_reply = "User 用户: " + user.full_name + " ID: " + str(user.id) + " Reported 举报了\nUser 用户: " + reply_user.full_name + " ID: " + str(reply_user.id) + "\nReported Content 被举报内容:\n" + vio_text
            message.reply_text(bot_reply)
    else:   #提示举报命令需要回复另一条信息
        message.reply_text("To submit a report, please reply to the message in violation of our policy and type /r in text body" + "\n若举报违规行为，请回复违规信息并在回复信息中键入 /r")

def add_dispatcher(dp):
    dp.add_handler(CommandHandler("r", report_command))
    return []