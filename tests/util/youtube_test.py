from util import youtube


def test_get_info():
    # 测试一分钟音乐
    info = youtube.get_info('https://www.youtube.com/watch?v=kYEC7bm7gFs')
    assert info['title'] == '【一分鐘音樂】一分鐘足夠感動你 「冬·憶 Winter Memories」 原創鋼琴純音樂 Original Piano Music'
    assert info['duration'] == 60.0
    assert len(info['formats']) == 24
    # 测试4K视频
    info = youtube.get_info('https://www.youtube.com/watch?v=1PTs1mqrToM')
    assert info['title'] == 'Brazil 4K - Scenic Relaxation Film With Calming Music'
    assert info['duration'] == 3637
    assert len(info['formats']) == 25


def test_download_youtube():
    # 测试音乐title中有/的情况
    r, path = youtube.download_youtube(
        'https://www.youtube.com/watch?v=YD4dea4RD1E', '/tmp/')
    assert r == True
    assert path == '/tmp/slash Punctuation_ full stop Punctuation ..YD4dea4RD1E.m4a'
    # 测试音乐文件过大
    r, path = youtube.download_youtube(
        'https://www.youtube.com/watch?v=1PTs1mqrToM', '/tmp/')
    assert r == False
    assert path == '您要下载的音乐竟然有21MB之大，这是要撑爆Telegram的节奏啊！'


def test_search():
    url = youtube.search('【一分鐘音樂】一分鐘足夠感動你')
    assert url == 'https://youtube.com/watch?v=kYEC7bm7gFs'
