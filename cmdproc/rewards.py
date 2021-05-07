from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from random import randint

def rewards_cmd(update: Update, _: CallbackContext) -> None:
    member = update.message.from_user.full_name
    print(member)
    a=randint(0,200)
    print(a)
    if a ==0:
        update.message.reply_text("亲爱的" + member + ",你很惨! 不要放弃！ 继续努力！加油啊")
    else:
        update.message.reply_text("亲爱的" + member + ",恭喜您获得积分奖励"+ str(a) + "xp!")

def add_dispatcher(dp):
    dp.add_handler(CommandHandler("rewards", rewards_cmd))
    return []




    
    