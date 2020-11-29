# -*- coding: utf-8 -*-
# @Time : 2020/11/29
# @Author : lvaohui
# @File : download_video.py
# @Software: PyCharm

import requests,sys,time,os
from contextlib import closing


cookie = "" # 登陆后的Cookie，不填只能下载480P以下清晰度的
video_urls = ["https://www.bilibili.com/video/BV1gp4y1e7L5","BV1gp4y1e7L5"] # 视频链接或bvid列表
quality = "112" #清晰度 112/1080P+,80/1080P,64/720P,32/480P,16/360P
save_path = "./videos" #保存下载视频的文件夹路径


def main():
    for video_url in video_urls:
        bvid = video_url[video_url.rfind("/")+1:]
        videos = get_video_title_url(bvid)
        for video in videos: # 有多P下多P
            download_video(video["title"],video["download_url"],bvid)


def get_video_title_url(bvid):
    """
    得到视频标题和下载链接
    :param bvid: 例：BV1Xi4y1V7cf
    :return:
    """
    videos = [] # 存有视频信息的列表 {"title":"","download_url":""}
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}" # 获取视频标题和cid信息
    response = session.get(url).json()
    for page in response['data']['pages']:
        cid = page['cid']
        url = f"https://api.bilibili.com/x/player/playurl?cid={cid}&otype=json&qn={quality}&bvid={bvid}" # 获取单个cid的下载链接
        resp = session.get(url).json()
        print(resp)
        download_url = resp['data']['durl'][0]['url']
        videos.append({
            "title":response['data']['title'],
            "download_url":download_url
        })
        if response['data']['videos']>1: # 如果有多P加上副标题
            videos[-1]["title"] += "-" + page['part']
    return videos


def download_video(title,download_url,bvid):
    """
    下载视频
    :param title: 标题
    :param download_url: 下载链接
    :param bvid:
    :return:
    """
    session.headers["referer"] = f"https://www.bilibili.com/video/{bvid}"
    st_time = time.time()
    with closing(session.get(download_url, stream=True)) as response:
        chunk_size = 1024  # 单次请求最大值
        total_size = int(response.headers['content-length'])  # 内容体总大小
        temp_size = 0
        with open(f"{save_path}/{title}.mp4", "wb") as f:
            for data in response.iter_content(chunk_size=chunk_size):
                if data:
                    ed_time = time.time()
                    temp_size += len(data)
                    f.write(data)
                    f.flush()
                    # 进度条
                    done = int(50 * temp_size / total_size)
                    sys.stdout.write(f"\r{title}：[{'█' * done}{' ' * (50 - done)}] {round(100 * temp_size / total_size,2)}% {round(temp_size/1024/(ed_time-st_time),2)} KB/s")
                    sys.stdout.flush()
        print()


if __name__ == '__main__':
    save_path = save_path.rstrip('/\\')
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    session = requests.Session()
    session.headers = {
        "Cookie":cookie,
        "Connection": "keep-alive",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
    }
    main()
