from telegram import User,Message
from telegram.ext import CallbackContext
from telegram.utils.helpers import escape_markdown

def get_user_link(from_user:User) -> str:
    return f"[{escape_markdown(from_user.first_name,2)}](tg://user?id={from_user.id})"

def delete_reply_msg(context : CallbackContext):
    msg=context.job.context
    context.bot.delete_message(msg.chat.id,msg.message_id)

def delay_del_msg(context : CallbackContext , msg : Message, delay : int):
    context.job_queue.run_once(delete_reply_msg,delay,context=msg,name=f"delete_msg_{msg.message_id}")