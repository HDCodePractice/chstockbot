from telegram import Update,  BotCommand
from telegram.ext import CommandHandler,  CallbackContext

def delete_reply_msg(context : CallbackContext):
    msgs=context.job.context
    for msg in msgs:
        context.bot.delete_message(msg.chat.id,msg.message_id)

def group_command(update: Update, context: CallbackContext) -> None:
    delete_time = 30
    if update.effective_chat.id == -1001346239262: 
        # 主群的回复
       msg = update.message.reply_text("""
精华收集频道-毛票教友汇
https://t.me/joinchat/TfWBdbo2jPd-rsRH

夕阳红躁动的天像
https://t.me/joinchat/XBRB50LT75swMWJl

毛毛投的朋友们
https://t.me/joinchat/8x3bZvMMVmliNmY1

旅行团友群：
https://t.me/joinchat/H7BPD0eLWqvSTPKB

狼人杀现场：
https://t.me/joinchat/H3E3Y_WL4MABeF9s

Switch游戏玩不停
https://t.me/joinchat/6OHFklcv-8JlZmM1

两个财经快讯频道
https://t.me/cnwallstreet
https://t.me/fnnew
       """,disable_web_page_preview=True)
       context.job_queue.run_once(delete_reply_msg,delete_time,context=[msg,update.effective_message],name=f"delete_msg_{msg.message_id}")
    else: # 私聊时发送标准的内容回去
       msg = update.message.reply_text(
"""欢迎你来到寻找毛票教的仙踪

<b>进群后请主动说话，不说话的很快就会被踢出来的</b>

精华收集频道-毛票教友汇
https://t.me/joinchat/TfWBdbo2jPd-rsRH

夕阳红躁动的天像
https://t.me/joinchat/XBRB50LT75swMWJl

毛毛投的朋友们
https://t.me/joinchat/8x3bZvMMVmliNmY1

股票开心聊群：
https://t.me/joinchat/CpWBiw6yHOkyYTVl

旅行团友群：
https://t.me/joinchat/H7BPD0eLWqvSTPKB

狼人杀现场：
https://t.me/joinchat/H3E3Y_WL4MABeF9s

Switch游戏玩不停
https://t.me/joinchat/6OHFklcv-8JlZmM1""",disable_web_page_preview=True)
    context.job_queue.run_once(delete_reply_msg,delete_time,context=[msg,update.effective_message],name=f"delete_msg_{msg.message_id}")


def delete_reply_msg(context : CallbackContext):
    msgs=context.job.context
    for msg in msgs:
        context.bot.delete_message(msg.chat.id,msg.message_id)

def add_dispatcher(dp):
    dp.add_handler(CommandHandler(["start","help"], group_command))
    return [BotCommand('help','获得神秘代码')]
