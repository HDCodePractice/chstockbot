from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import random

#1 direct call array
good_rewards_array = ["So Great!", "Awesome Reward for you!", "Nice!","Perfect","You did great job!","Good gift for you!","You earn something great!","Wow, this is amazing","You deserve it!"]
bad_rewards_array = ["oh no..", "So sorry...", "bad luck...", "next time will be better..", "May be next time"]
#2 build data.json file and read data from file


def reward_cmd(update: Update, _:CallbackContext):
    rewardNumber = random.randint(0,200) #get random number from 0 - 200
    print(rewardNumber)

    if rewardNumber == 0 :
        badRewardWordIndex = random.randint(0,len(bad_rewards_array) - 1) #get random index from bad words list
        print(badRewardWordIndex)
        #get value of index from bad words list
        update.message.reply_text(bad_rewards_array[badRewardWordIndex] + "! You got " + str(rewardNumber) + " XP! ")
    else :
        goodRewardWordIndex = random.randint(0,len(good_rewards_array) - 1) #get random index from good words list
        print(goodRewardWordIndex)
         #get value of index from good words list
        update.message.reply_text(good_rewards_array[goodRewardWordIndex] + "! You got " + str(rewardNumber) + " XP! ")

def add_dispatcher(dp):
    dp.add_handler(CommandHandler("rewards", reward_cmd))
    return []