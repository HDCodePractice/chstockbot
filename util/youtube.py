from youtube_dl import YoutubeDL
import json, asyncio,os
class YoutubeDLError(Exception):
    pass


def download_youtube(url,path="~/Downloads/"):
    err_msg = ""
    youtube,url_info_list = get_info(url) #get id/ext information
    #print(json.dumps(url_info_list))
    if url_info_list["filesize"] > 10485760 : #判断文件大小
        err_msg = "您要下载的文件太大了，请重新选择"
    else:
        try:
            #loop = asyncio.get_event_loop()
            #await loop.run_in_executor(None, youtube.download, [url])
            dl_file = youtube.download([url]) #download music
            if dl_file == 0:
                return True, f"{url_info_list['title']}.{url_info_list['id']}.{url_info_list['ext']}"
        except Exception as e:
            err_msg = f"音乐下载报错了，具体错误是{e}"
    return False, err_msg

def get_info(url):
    ydl_opts = {
    "format": "worstaudio[ext=m4a]",
    "geo-bypass": True,
    "nocheckcertificate": True,
    "outtmpl": "%(title)s.%(id)s.%(ext)s",
    "continuedl" : True
    }
    youtube = YoutubeDL(ydl_opts)
    try:
        info = youtube.extract_info(url, download=False)
    except Exception as e:
        return None
    formats = info["formats"]
    thumbnails = info["thumbnails"]
    title = info["title"]
    duration = info["duration"]
    return youtube,info


if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=kYEC7bm7gFs"
    #url = "https://www.youtube.com/watch?v=1PTs1mqrToM"
    print(get_info(url))