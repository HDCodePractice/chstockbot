from telegram import Update,  BotCommand
from telegram.ext import CommandHandler,  CallbackContext

def group_command(update: Update, context: CallbackContext) -> None:
    delete_time = 30
    if update.effective_chat.id == -1001346239262: 
        # 主群的回复
       msg = update.message.reply_text("""
旅行团友群：
https://t.me/joinchat/H7BPD0eLWqvSTPKB

狼人杀现场：
https://t.me/joinchat/H3E3Y_WL4MABeF9s

Switch游戏玩不停
https://t.me/joinchat/6OHFklcv-8JlZmM1

本群精华收集频道-听毛票女神和女皇的
https://t.me/joinchat/TfWBdbo2jPd-rsRH

ARK交易跟踪频道
https://t.me/ark_fyi_bot
https://t.me/ARK_Trading_Desk
https://ark.alien-tomato.com/

两个财经快讯频道
https://t.me/cnwallstreet
https://t.me/fnnew

一本书读懂K线图，图形技术入门书
https://t.me/c/1307935093/97

麦克米伦谈期权，读完之后再考虑操作期权
https://t.me/c/1307935093/95

期权、期货及其他衍生产品，读完之后再考虑操作期货
https://t.me/c/1307935093/96
       """,disable_web_page_preview=True)
       context.job_queue.run_once(delete_reply_msg,delete_time,context=[msg,update.effective_message],name=f"delete_msg_{msg.message_id}")
    else: # 私聊时发送标准的内容回去
       update.message.reply_text(
"""欢迎来自clubhouse的朋友
股票开心聊群：
https://t.me/joinchat/CpWBiw6yHOkyYTVl

旅行团友群：
https://t.me/joinchat/H7BPD0eLWqvSTPKB

狼人杀现场：
https://t.me/joinchat/H3E3Y_WL4MABeF9s

Switch游戏玩不停
https://t.me/joinchat/6OHFklcv-8JlZmM1""",disable_web_page_preview=True)


def delete_reply_msg(context : CallbackContext):
    msgs=context.job.context
    for msg in msgs:
        context.bot.delete_message(msg.chat.id,msg.message_id)

def add_dispatcher(dp):
    dp.add_handler(CommandHandler(["start","help"], group_command))
    return [BotCommand('help','获得神秘代码')]
