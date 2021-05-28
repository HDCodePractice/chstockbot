from telegram import Update,  BotCommand
from telegram.ext import CommandHandler,  CallbackContext

vio_text = "举报信息"
admingroup = -1001250988031
groups =[-1001409640737,-1001250988031]
#print(groups[1])

def report_command(update: Update, _: CallbackContext) -> None:
    message = update.message
    user = message.from_user
    reply_user = message.reply_to_message.from_user
    if message.reply_to_message != None:     #检查举报命令否为回复信息
        if message.reply_to_message.text == None:    #检查被举报的信息内容是否为文本信息
            vio_text = "非文本信息" #若被举报信息不含文本则定义举报内容为非文本信息                         
        else:                
            vio_text = message.reply_to_message.text #赋值被举报信息
            bot_reply = f"""
User 用户: {user.full_name}  ID: {user.id} Reported 举报了
User 用户: {reply_user.full_name} ID: {reply_user.id}
Reported Content 被举报内容:
{vio_text}"""
            bot = update.effective_message.bot
            bot.send_message(groups[1],bot_reply)
            # message.reply_text(bot_reply)
    else:   #提示举报命令需要回复另一条信息
        message.reply_text("To submit a report, please reply to the message in violation of our policy and type /r in text body" + "\n若举报违规行为，请回复违规信息并在回复信息中键入 /r")

def kick_command(update: Update, _: CallbackContext) -> None:
    bot = update.effective_message.bot
    message = update.message.reply_text
    spammerId = message.split("\n")[1].split(" ID: ")[-1]
    #spammerName = message.split("\n")[1].split(" ID: ")[0].split(" 用户： ").[-1]
    bot.kick_chat_member(groups[0],spammerId)
    bot.unban_chat_member(groups[0],spammerId)            
    bot.send_message(groups[1],f"""User {spammerName} is removed from group groups[0].""")

def kickreporter_command(update: Update, _: CallbackContext) -> None:
    bot = update.effective_message.bot
    message = update.message.reply_text
    reporterId = message.split("\n")[0].split(" ID: ")[1].split(" Reported ")[0].split(" ID ")[-1]
    reporterName = message.split("\n")[0].split(" ID: ")[1].split(" 用户: ")[-1]
    bot.kick_chat_member(groups[0],reporterId)
    bot.unban_chat_member(groups[0],reporterId)
    bot.send_message(groups[1],f"""User {reporterName} is removed from group groups[0].""")


def add_dispatcher(dp):
    dp.add_handler(CommandHandler("r", report_command))
    dp.add_handler(CommandHandler("k", kick_command))
    dp.add_handler(CommandHandler("kr", kickreporter_command))
    return [BotCommand('r','举报一个对话'),BotCommand('k','🦶一个人出群！'),BotCommand('kr','🦶一个举报人出群！')]