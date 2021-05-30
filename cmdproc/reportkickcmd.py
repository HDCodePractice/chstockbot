from telegram import Update, ForceReply, BotCommand, bot, replykeyboardmarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


 
def report_command(update: Update, context:CallbackContext) -> None:
    print(update)
    reporter = update.message.from_user.full_name
    print(reporter)
    reporterId = update.message.from_user.id
    print(reporterId)
    scammer = update.message.reply_to_message.from_user.full_name
    print(scammer)
    scammerId = update.message.reply_to_message.from_user.id
    print(scammerId)
    message_reply= update.message.reply_to_message.text
    

    update.message.reply_text(f"""
name: {reporter} id: {reporterId} 举报了~ 
name: {scammer} id: {scammerId}说了 
{message_reply}""")
    

    admin_chat_id = -100xxxxxx
    groups = [-100yyyyyy, --100zzzzzz]
    from_chat_id = update.message.reply_text.chat_id
    reply_text_message_id = update.message.reply_text.message_id

    bot.forward_message(f"""{admin_chat_id} {from_chat_id}, {reply_text_message_id}""", 
                        disable_notification=None, timeout=None, api_kwargs=None) 
                         

def kr_command(update: Update, context:CallbackContext) -> None:
    print(update)
    reporter = update.message.from_user.full_name
    print(reporter)
    reporterId = update.message.from_user.id
    print(reporterId)
    scammer = update.message.reply_to_message.from_user.full_name
    print(scammer)
    scammerId = update.message.reply_to_message.from_user.id
    print(scammerId)
    message_reply= update.message.reply_to_message.text
    groups = [-100yyyyyy, --100zzzzzz]

    bot.kick_chat_member(f"""{groups} {reporterId}""", timeout=None, 
                        until_date=None, api_kwargs=None, revoke_messages=None)

def kk_command(update: Update, context:CallbackContext) -> None:
    print(update)
    reporter = update.message.from_user.full_name
    print(reporter)
    reporterId = update.message.from_user.id
    print(reporterId)
    scammer = update.message.reply_to_message.from_user.full_name
    print(scammer)
    scammerId = update.message.reply_to_message.from_user.id
    print(scammerId)
    message_reply= update.message.reply_to_message.text
    groups = [-100yyyyyy, --100zzzzzz]

    bot.kick_chat_member(f"""{groups} {scammerId}""", timeout=None, 
                        until_date=None, api_kwargs=None, revoke_messages=None)


def unban_command(update: Update, context:CallbackContext) -> None:
    print(update)
    groups = [-100yyyyyy, --100zzzzzz]
    unbannerId=update.message.from_user.id #如果获得unbannerID?

    bot.unban_chat_member(f"""{unbannerId} {unbannerId}""")


def add_dispatcher(dp):
    dp.add_handler(CommandHandler("r", report_command))
    dp.add_handler(CommandHandler("kr", kr_command))
    dp.add_handler(CommandHandler("kk", kk_command))
    dp.add_handler(CommandHandler("unban", unban_command))
    return [BotCommand('r','举报一个对话'),BotCommand('kr','将‘被’举报人踢出群并拉黑'),BotCommand('kk','将举报人踢出群并拉黑')]