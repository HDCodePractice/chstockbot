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
毛票教友汇频道
https://t.me/joinchat/r8M60eytJVY1MjZl

夕阳红频道
https://t.me/joinchat/XBRB50LT75swMWJl

毛毛投频道
https://t.me/joinchat/8x3bZvMMVmliNmY1

旅行团友群：
https://t.me/joinchat/H7BPD0eLWqvSTPKB

狼人杀现场：
https://t.me/joinchat/H3E3Y_WL4MABeF9s

Switch游戏玩不停
https://t.me/joinchat/6OHFklcv-8JlZmM1

如果你认为群里有人发出了让你不满的消息让你非常不舒服，或是有人私信你你认为不应该让他再打扰更多群友，欢迎举报相关人员：
https://t.me/c/1307935093/367
       """,disable_web_page_preview=True)
       context.job_queue.run_once(delete_reply_msg,delete_time,context=[msg,update.effective_message],name=f"delete_msg_{msg.message_id}")
    else: # 私聊时发送标准的内容回去
       msg = update.message.reply_text(
"""欢迎你来到寻找毛票教的仙踪

本教相关频道和群都暂进不对外开放，如果想加入请联系已经在群里的朋友，让管理员给你一个进群的邀请。
""",disable_web_page_preview=True)
    context.job_queue.run_once(delete_reply_msg,delete_time,context=[msg,update.effective_message],name=f"delete_msg_{msg.message_id}")


def delete_reply_msg(context : CallbackContext):
    msgs=context.job.context
    for msg in msgs:
        context.bot.delete_message(msg.chat.id,msg.message_id)

def add_dispatcher(dp):
    dp.add_handler(CommandHandler(["start","help"], group_command))
    return [BotCommand('help','获得神秘代码')]
