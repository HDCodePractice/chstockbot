from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import random

def rewardcmd(update: Update, _: CallbackContext) -> None:
    a = random.randint(0,201,10)
    b = random.choice(['咦，有点惨\nOh, sorry','恭喜贺喜！\nCongratulations!',
    '太厉害了！\nAwesome!','您的运气太好了，牛气冲天啊！\nYou are so lucky!'])
    if a >= 1:
        update.message.reply_text(b + '\n您得到了'+ str(a) +'点奖励！'
        '\nThis time, you get ' + str(a) +' credits!')
    else:
        update.message.reply_text("继续努力哦 :)\nWish you luch next time. :)")

def add_dispatcher(dp):
    dp.add_handler(CommandHandler("reward", rewardcmd))
    return []


