from typing import List, Union
from pyrogram import filters
from ..config import BOT_USERNAME

def command(commands: Union[str, List[str]]):
    cmds = []
    if isinstance(commands,list):
        for cmd in commands:
            cmds.append(cmd)    
            cmds.append(f"{cmd}@{BOT_USERNAME}")
    else:
        cmds.append(commands)
        cmds.append(f"{commands}@{BOT_USERNAME}")
    return filters.command(cmds)