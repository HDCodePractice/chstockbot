from telegram import Update,  BotCommand, error
from telegram.ext import CommandHandler,  CallbackContext
from telegram.error import BadRequest, TelegramError

vio_text = "举报信息"
admingroup = -1001250988031
groups =[-1001409640737,-1001430794202,-1001484528239]

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
            bot.send_message(admingroup,bot_reply)
            # message.reply_text(bot_reply)
    else:   #提示举报命令需要回复另一条信息
        message.reply_text("To submit a report, please reply to the message in violation of our policy and type /r in text body" + "\n若举报违规行为，请回复违规信息并在回复信息中键入 /r")

def kk_command(update: Update, _: CallbackContext) -> None:
    bot = update.effective_message.bot
    reply_message_from_report = update.message.reply_to_message.text
    scammerId = reply_message_from_report.split("\n")[1].split(" ID: ")[-1]
    scammer_name = reply_message_from_report.split("\n")[1].split(" ID: ")[0].split(" 用户: ")[-1]
    group_title = update.message.chat.title
    
    bot_reply = ""
    for g in groups:
        try:
            bot.kick_chat_member(g,scammerId)
            bot.unban_chat_member(g,scammerId)
            bot_reply += f""" {scammer_name} has been removed from {group_title}: {g} \n"""
        except TelegramError as error:
            bot_reply += f"""
        {scammer_name} do not exist in {group_title}: {g}
        error info: {error}\n"""
    bot.send_message(admingroup,bot_reply)

def kr_command(update: Update, _: CallbackContext) -> None:
    bot = update.effective_message.bot
    reply_message_from_report = update.message.reply_to_message.text
    reporterId = reply_message_from_report.split("\n")[0].split(" ID: ")[-1].split(" reported ")[0]
    reporter_name = reply_message_from_report.split("\n")[0].split(" ID: ")[0].split(" 用户: ")[-1]
    group_title = update.message.chat.title

    for g in groups:
        try:
            bot.kick_chat_member(g,reporterId)
            bot.unban_chat_member(g,reporterId)
            bot_reply = f""" {reporter_name} has been removed from {group_title}: {g}"""
            bot.send_message(admingroup,bot_reply)
        except:
            error =error.badrequest
            update.message.reply_text(f"""
        {reporter_name} do not exist in {group_title}: {g}
        error info: {error}""")

def add_dispatcher(dp):
    dp.add_handler(CommandHandler("r", report_command))
    dp.add_handler(CommandHandler("kk", kk_command))
    dp.add_handler(CommandHandler("kr", kr_command))
    return [BotCommand('r','举报一个对话'),BotCommand('kk','🦶一个人出群！'),BotCommand('kr','🦶一个人出群！')]