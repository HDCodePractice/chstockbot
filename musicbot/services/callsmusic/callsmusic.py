from typing import Dict

from pytgcalls import GroupCall

from . import client
from .. import queues
from ..modules import control
import os

instances: Dict[int, GroupCall] = {}
active_chats: Dict[int, Dict[str, bool]] = {}


def init_instance(chat_id: int):
    if chat_id not in instances:
        instances[chat_id] = GroupCall(client)
        instances[chat_id].play_on_repeat = False

    instance = instances[chat_id]

    @instance.on_playout_ended
    async def ___(__, _):
        queues.task_done(chat_id)
        if queues.is_empty(chat_id):
            # 如果队列里的内容没有了，退出
            # await stop(chat_id)
            file = instance.input_filename
            try:
                os.remove(file)
            except FileNotFoundError as err:
                # 不知道为什么，播放完之后会调用两次on_playout_ended
                print(err)
            await control.clean(chat_id)
        else:
            song = queues.get(chat_id)
            instance.input_filename = song['file']
            await control.send_photo(
                chat_id,
                song['thumbnail'],
                caption=f"正在播放 {song['user'].first_name} 点播的\n`{song['title']}` by `{song['singers']}` {song['sduration']}\n 还有 {queues.qsize(chat_id)} 待播放")



def remove(chat_id: int):
    if chat_id in instances:
        del instances[chat_id]

    if not queues.is_empty(chat_id):
        queues.clear(chat_id)

    if chat_id in active_chats:
        del active_chats[chat_id]


def get_instance(chat_id: int) -> GroupCall:
    init_instance(chat_id)
    return instances[chat_id]


async def start(chat_id: int):
    await get_instance(chat_id).start(chat_id)
    active_chats[chat_id] = {'playing': True, 'muted': False}


async def stop(chat_id: int):
    await get_instance(chat_id).stop()

    if chat_id in active_chats:
        del active_chats[chat_id]
    await control.init_instances(chat_id)    


async def set_stream(chat_id: int, file: str):
    if chat_id not in active_chats:
        await start(chat_id)
    get_instance(chat_id).input_filename = file
    song = queues.get(chat_id)
    await control.send_photo(
        chat_id,
        song['thumbnail'],
        caption=f"正在播放 {song['user'].first_name} 点播的\n`{song['title']}` by `{song['singers']}` {song['sduration']}\n 还有 {queues.qsize(chat_id)} 待播放")

def pause(chat_id: int) -> bool:
    if chat_id not in active_chats:
        return False
    elif not active_chats[chat_id]['playing']:
        return False

    get_instance(chat_id).pause_playout()
    active_chats[chat_id]['playing'] = False
    return True


def resume(chat_id: int) -> bool:
    if chat_id not in active_chats:
        return False
    elif active_chats[chat_id]['playing']:
        return False

    get_instance(chat_id).resume_playout()
    active_chats[chat_id]['playing'] = True
    return True


def mute(chat_id: int) -> int:
    if chat_id not in active_chats:
        return 2
    elif active_chats[chat_id]['muted']:
        return 1

    get_instance(chat_id).set_is_mute(True)
    active_chats[chat_id]['muted'] = True
    return 0


def unmute(chat_id: int) -> int:
    if chat_id not in active_chats:
        return 2
    elif not active_chats[chat_id]['muted']:
        return 1

    get_instance(chat_id).set_is_mute(False)
    active_chats[chat_id]['muted'] = False
    return 0
