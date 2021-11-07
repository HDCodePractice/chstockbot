from youtube_dl import YoutubeDL
import json, asyncio,os
class YoutubeDLError(Exception):
    pass

def download_youtube(url,path="~/Downloads/"):
    ydl_opts = {
        "format": "worstaudio[ext=m4a]",
        "geo-bypass": True,
        "nocheckcertificate": True,
        "outtmpl": path + "%(title)s.%(id)s.%(ext)s",
        "continuedl" : True
    }
    err_msg = ""
    youtube = YoutubeDL(ydl_opts) #init youtube-dl
    url_info_list = youtube.extract_info(url, download=False) #get id/ext information
    #print(json.dumps(url_info_list))
    if url_info_list["filesize"] > 10485760 : #判断文件大小
        err_msg = "您要下载的文件太大了，请重新选择"
    else:
        try:
            #loop = asyncio.get_event_loop()
            #await loop.run_in_executor(None, youtube.download, [url])
            dl_file = youtube.download([url]) #download music
            if dl_file == 0:
                return True, path + f"{url_info_list['title']}.{url_info_list['id']}.{url_info_list['ext']}"
        except Exception as e:
            err_msg = f"音乐下载报错了，具体错误是{e}"
    return False, err_msg




