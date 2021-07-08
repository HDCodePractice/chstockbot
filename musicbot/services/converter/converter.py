import asyncio
from os import path,remove

from musicbot.helpers.errors import FFmpegReturnCodeError

import ffmpeg

async def convert(file_path: str) -> str:
    out = path.join('raw_files', path.basename(file_path + '.raw'))
    if path.isfile(out):
        return out
    ffmpeg.input(file_path).output(
        out,
        format='s16le',
        acodec='pcm_s16le',
        ac=2,
        ar='48k'
    ).overwrite_output().run()
    remove(file_path)
    return out

# async def convert(file_path: str) -> str:
#     out = path.join('raw_files', path.basename(file_path + '.raw'))
#     if path.isfile(out):
#         return out
#     proc = await asyncio.create_subprocess_shell(
#         cmd=(
#             'ffmpeg '
#             '-y -i '
#             f'{file_path} '
#             '-f s16le '
#             '-ac 2 '
#             '-ar 44100 '
#             '-acodec pcm_s16le '
#             f'{out}'
#         ),
#         stdin=asyncio.subprocess.PIPE,
#         stderr=asyncio.subprocess.PIPE,
#     )
#     await proc.communicate()
#     if proc.returncode != 0:
#         raise FFmpegReturnCodeError('FFmpeg did not return 0')
#     return out