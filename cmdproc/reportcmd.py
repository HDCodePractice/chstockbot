from telegram import Update, BotCommand, ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.user import User
from config import ENV
from util.tgutil import get_user_link, delay_del_msg, get_group_info

admingroup = ENV.ADMIN_GROUP
groups = ENV.GROUPS
admins = ENV.ADMINS

def report_user(update: Update, context:CallbackContext):
    incoming_message = update.effective_message
    reportee_id = False  # 被举报人的id是否存在
    if update.effective_chat.id == update.effective_message.from_user.id:  
        # 私聊举报
        if update.effective_message.reply_to_message:
            # 私聊只接受转发来的消息
            reporter = update.effective_message.from_user
            report_msg = update.effective_message.reply_to_message
            if update.effective_message.reply_to_message.forward_from:
                # 开放了自己的信息给第三方
                reportee = update.effective_message.reply_to_message.forward_from
                reportee_id = True
            else:
                # 完全不开放自己的信息给第三方
                reportee = update.effective_message.reply_to_message.forward_sender_name
        else:
            # 直接发的/r或是不是回复的转发的消息
            incoming_message.reply_text("请把你要举报的人发给你的消息，转发给我后，再回复转发的消息 /r 进行举报")
            return
    elif str(update.effective_chat.id) in groups:
        # 在群中举报
        if incoming_message.reply_to_message:
            reporter = incoming_message.from_user #举报人信息
            reportee = incoming_message.reply_to_message.from_user #被举报人信息
            report_msg = incoming_message.reply_to_message #举报信息
        else:
            # 直接发的/r无效
            incoming_message.reply_text("请回复要举报的消息，直接举报是无效的")
            return
    else:
        # 不是私聊，不是指定的群，什么都不做
        return
    if isinstance(reportee,User) and reporter.id == reportee.id:
        # 不能举报自己
        incoming_message.reply_text("咱能不举报自己玩儿吗？")
        return
    # 收到举报，处理举报
    # 先把原来的消息转发到管理群
    try:
        no_forward = False
        msg = report_msg.forward(admingroup, disable_notification=True) 
    except BadRequest:
        no_forward = True
    # 给出踢人的提示
    msg_text = f"被举报人：{reportee if isinstance(reportee,str) else get_user_link(reportee)} 举报人：{get_user_link(reporter)}\n请仔细检查举报信息，决定是否处理举报。"
    reportee_id = "null" if isinstance(reportee,str) else reportee.id
    reportee_name = reportee if isinstance(reportee,str) else reportee.first_name
    # 在callback_data里加入被举报人的id和举报人的名字，举报人干掉的按钮里，后为0
    keyboard = [[
        InlineKeyboardButton(text=f"干掉{reportee_name}", callback_data=f"kick:{reportee_id}:{reporter.id}"),
        InlineKeyboardButton(text=f"干掉{reporter.first_name}", callback_data=f"kick:{reporter.id}:0")
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    if no_forward:
        # 如果没有转发，就把消息发到管理群
        context.bot.send_message(chat_id=admingroup, text=msg_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        msg.reply_markdown_v2(msg_text,reply_markup=reply_markup)
    send_msg = incoming_message.reply_text(f"""亲爱的{reporter.full_name}: 你的举报已成功，感谢你的一份贡献\n\n贡献者:毛票教的大朋友们""")   
    delay_del_msg(context,incoming_message,10)
    delay_del_msg(context,send_msg,10)

def kick_user(update: Update, context:CallbackContext):
    kick_user,report_user = update.callback_query.data.split('kick:')[1].split(':')
    if str(update.effective_user.id) not in admins:
        update.callback_query.answer(text="哥们，你还不是管理员，请升级为管理员后再按～",show_alert=True)
        return
    if kick_user == "null":
        update.callback_query.answer(text="Bot无法获取这个人的信息，需要你按他的",show_alert=True)
        return
    count = 0
    kick_count = 0
    kick_group = []
    kick_group_msg = ""
    for group in groups:
        count += 1
        try:
            cm = context.bot.get_chat_member(group,kick_user)
            if cm.status == cm.MEMBER:
                if not ENV.DEBUG:
                    context.bot.ban_chat_member(group,kick_user,revoke_messages=True)
                kick_count += 1
                kick_group.append(context.bot.get_chat(group))
        except BadRequest:
            context.bot.send_message(admingroup,f"Bot在{group}里不是管理员")
    kick_user = context.bot.get_chat(kick_user)
    for group in kick_group:
        kick_group_msg += f"{get_group_info(group)}\n"
    context.bot.send_message(
        admingroup,
        f" {get_user_link(update.effective_user)} 把 {get_user_link(kick_user)} 从毛票教{count}个群中的{kick_count}个群:\n{kick_group_msg}轻轻的碾压出去了",
        parse_mode=ParseMode.MARKDOWN_V2)
    if report_user == "0":
        response = f"由于恶意举报，您已被移除出群！"
    else:
        response = f"您的举报已经被管理员处理，感谢您的贡献！"
    context.bot.send_message(
        update.effective_user.id,
        response
    )

def add_dispatcher(dp):
    dp.add_handler(CommandHandler("r", report_user))
    dp.add_handler(CallbackQueryHandler(kick_user,pattern="^kick:[A-Za-z0-9_-]*"))
    return [BotCommand('r','举报SPAM行为')]
