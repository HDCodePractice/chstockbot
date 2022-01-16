import asyncio
import json
import os

from yt_dlp import YoutubeDL


class YoutubeDLError(Exception):
    pass


def init_yt(ydl_opts=None, download_path="assets"):
    ydl_opts = {
        "format": "worstaudio[ext=m4a]",
        "geo-bypass": True,
        "nocheckcertificate": True,
        "outtmpl": f"{download_path}/%(id)s.%(ext)s",
        "continuedl": True
    }
    youtube = YoutubeDL(ydl_opts)
    return youtube


def download_youtube(url, download_path="assets"):
    err_msg = ""
    youtube = init_yt(download_path=download_path)
    try:
        dl_file = youtube.download([url])  # download music
        if dl_file == 0:
            return True, None
    except Exception as e:
        err_msg = f"音乐下载报错了，具体错误是{e}"
    return False, err_msg


def get_info(url):
    youtube = init_yt()
    try:
        info = youtube.extract_info(url, download=False)
        info["waiting_time"] = (info["filesize"]/1024/info["tbr"]
                                ) if "tbr" in info.keys() else (info["filesize"]/1024/info["abr"])
    except Exception as e:
        return None
    formats = info["formats"]
    thumbnails = info["thumbnails"]
    title = info["title"]
    duration = info["duration"]
    return info
