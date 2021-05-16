from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def rewards_cmd(update: Update, _: CallbackContext) -> None:
    member = update.message.from_user.full_name
    import random
    n = random.randint(0,200)
    if n == 0:
        update.message.reply_text("Oh no " + member + "你没有得到任何奖励噢 惨惨猪!")
    elif n <= 100:
        update.message.reply_text("不错哟 " + member + "拿到" + str(n) + "xp的奖励噢！")
    elif n < 200:
        update.message.reply_text("耶耶 " + member + "拿到" + str(n)+ "xp的奖励噢！")
    else:
        update.message.reply_text("哇塞 " + member + "拿到最高xp的奖励噢！")


def add_dispatcher(dp):
    dp.add_handler(CommandHandler("rewards", rewards_cmd))
    return []

