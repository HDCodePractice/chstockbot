from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from random import randint, choice



def rewards_cmd(update: Update, _: CallbackContext) -> None:
    print(update)
    member = update.message.from_user.full_name
    print(member)
    a = randint(0,200)
    print(a)
    failure_line = choice(["你很惨! 不要放弃!","你很惨! 继续努力!", "你很惨! 加油啊!"])
    success_line = choice(["太棒了!", "再接再厉!", "下次会更好!"])
    if a == 0:
        update.message.reply_text(f"""亲爱的 {member} , {failure_line}""")
    else:
        update.message.reply_text(f"""亲爱的 {member} , 恭喜您获得积分奖励 str(a) xp! {success_line}""")

def add_dispatcher(dp):
    dp.add_handler(CommandHandler("rewards", rewards_cmd))
    return []




    
    