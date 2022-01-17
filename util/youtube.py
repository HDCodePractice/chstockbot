from youtube_search import YoutubeSearch
from yt_dlp import YoutubeDL


class YoutubeDLError(Exception):
    pass


def search(keyword):
    results = YoutubeSearch(keyword, max_results=1).to_dict()
    url = f"https://youtube.com{results[0]['url_suffix']}"
    return url


def init_yt(ydl_opts=None, download_path="assets"):

    ydl_opts = {
        "format": "worstaudio[ext=m4a]",
        "geo-bypass": True,
        "nocheckcertificate": True,
        "outtmpl": f"{download_path}/%(title)s.%(id)s.%(ext)s",
        "continuedl": True
    }
    youtube = YoutubeDL(ydl_opts)
    return youtube


def download_youtube(url, path="~/Downloads/"):
    if path[-1] != "/":
        path = path + "/"
    ydl_opts = {
        "format": "worstaudio[ext=m4a]",
        "geo-bypass": True,
        "nocheckcertificate": True,
        "outtmpl": path + "%(title)s.%(id)s.%(ext)s",
        "continuedl": True
    }
    err_msg = ""
    youtube = YoutubeDL(ydl_opts)  # init youtube-dl
    url_info_list = youtube.extract_info(
        url, download=False)  # get id/ext information
    if url_info_list["filesize"] > 20971520:  # 判断文件大小
        size = int(url_info_list["filesize"]/1024/1024)
        err_msg = f"您要下载的音乐竟然有{size}MB之大，这是要撑爆Telegram的节奏啊！"
    else:
        try:
            dl_file = youtube.download([url])  # download music
            if dl_file == 0:
                return True, youtube.prepare_filename(url_info_list)
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
