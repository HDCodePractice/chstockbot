import asyncio
from os import path

from youtube_dl import YoutubeDL

from musicbot.config import DURATION_LIMIT
from musicbot.helpers.errors import DurationLimitError

ydl_opts = {
    "format": "bestaudio[ext=m4a]",
    "geo-bypass": True,
    "nocheckcertificate": True,
    "outtmpl": "downloads/%(id)s.%(ext)s",
}

ydl = YoutubeDL(ydl_opts)

def download(url: str) -> str:
    info = ydl.extract_info(url, False)
    duration = round(info["duration"] / 60)

    if duration > DURATION_LIMIT:
        raise DurationLimitError(
            f"❌ 视频长度为 {duration} 分钟，超过了 {DURATION_LIMIT} 分钟的限制"
        )
    try:
        ydl.download([url])
    except:
        raise DurationLimitError(
            f"❌ 视频长度为 {duration} 分钟，超过了 {DURATION_LIMIT} 分钟的限制"
        )
    return path.join("downloads", f"{info['id']}.{info['ext']}")
