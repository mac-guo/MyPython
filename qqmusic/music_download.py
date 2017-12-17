import urllib.request
import os
import re
import time
import random

# =======全局设置========

# 音乐文件夹路径名称（下载时会在此路径下根据歌手名创建文件夹）
music_dir_path = 'C:/Users/Administrator/Desktop/新建文件夹 (2)/音乐/'

# 下载链接qq号（目前不知道有什么用，随便填一个真实QQ号）
url_qq_number = '349602330'

# 歌曲名过滤正则表达式
song_name_filter = r'\(.*Live.*\)|\(.*Demo.*\)|\(.*现场.*\)|\(.*Remix.*\)|\(.*Mix.*\)' \
                   r'|\(.*DJ.*\)|\(.*伴奏.*\)|\(.*纯音乐.*\)|\(.*Piano.*\)|\(.*钢琴.*\)|\(.*环绕.*\)'

# 最小下载等待间隔（秒）
download_min_time = 10

# 最大下载等待间隔（秒）
download_max_time = 30

# =======全局设置========

# 进度条
def Schedule(a,b,c):
    per = 100.0 * a * b / c
    if per > 100 :
        per = 100
    # print('%.2f%%' % per)

# 下载音乐
def download(url, filePath, fileName):
    local = os.path.join(filePath, fileName)
    urllib.request.urlretrieve(url, local, Schedule)
    print('下载完成：' + fileName)
    # 随机等待一定时间 10-30s
    randomNum = random.randint(download_min_time, download_max_time)
    print('休息' + str(randomNum) + '秒')
    print('\n')
    time.sleep(randomNum)


# 根据页码获取歌手列表
def getSingerListByPageNum(pageNum):
    singerListUrl = 'https://c.y.qq.com/v8/fcg-bin/v8.fcg?' + \
                    'channel=singer' + \
                    '&page=list' + \
                    '&key=all_all_all' + \
                    '&pagesize=100' + \
                    '&pagenum=' + str(pageNum) + \
                    '&g_tk=334781856' + \
                    '&jsonpCallback=GetSingerListCallback' + \
                    '&loginUin=' + url_qq_number + \
                    '&hostUin=0' + \
                    '&format=jsonp' + \
                    '&inCharset=utf8' + \
                    '&outCharset=utf-8' + \
                    '&notice=0' + \
                    '&platform=yqq' + \
                    '&needNewCode=0'
    response = urllib.request.urlopen(singerListUrl)
    singerListHtmlContent = response.read().decode(encoding="utf-8")
    singerList = []
    singerIdList = re.findall(r'"Fsinger_mid":"(.*?)","Fsinger_name"', singerListHtmlContent)
    singerNameList = re.findall(r'"Fsinger_name":"(.*?)","Fsinger_tag"', singerListHtmlContent)
    for i in range(len(singerIdList)):
        singerList.append(singerIdList[i] + '-' + singerNameList[i])
    return singerList


# 根据歌手id获取歌单列表
def getSongListBySingerId(singerId):
    songListUrl = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg?' + \
                    'g_tk=334781856' + \
                    '&jsonpCallback=MusicJsonCallbacksinger_track' + \
                    '&loginUin=' + url_qq_number + \
                    '&hostUin=0' + \
                    '&format=jsonp' + \
                    '&inCharset=utf8' + \
                    '&outCharset=utf-8' + \
                    '&notice=0' + \
                    '&platform=yqq' + \
                    '&needNewCode=0' + \
                    '&singermid=' + str(singerId) + \
                    '&order=listen' + \
                    '&begin=0' + \
                    '&num=30' + \
                    '&songstatus=1'
    response = urllib.request.urlopen(songListUrl)
    songListHtmlContent = response.read().decode(encoding="utf-8")
    totalSongSize = re.findall(r'"total":(\d+?)},', songListHtmlContent)[0]

    # 多少页  从0开始
    totalPage = int(int(totalSongSize) / 30)

    # 循环获取歌单
    songList = []
    for i in range(0, totalPage + 1):
        songListUrl = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg?' + \
                      'g_tk=334781856' + \
                      '&jsonpCallback=MusicJsonCallbacksinger_track' + \
                      '&loginUin=' + url_qq_number + \
                      '&hostUin=0' + \
                      '&format=jsonp' + \
                      '&inCharset=utf8' + \
                      '&outCharset=utf-8' + \
                      '&notice=0' + \
                      '&platform=yqq' + \
                      '&needNewCode=0' + \
                      '&singermid=' + str(singerId) + \
                      '&order=listen' + \
                      '&begin=' + str(i*30) + \
                      '&num=30' + \
                      '&songstatus=1'
        response = urllib.request.urlopen(songListUrl)
        songListHtmlContent = response.read().decode(encoding="utf-8")
        songIdList = re.findall(r'"strMediaMid":"(.+?)","stream"', songListHtmlContent)
        songNameList = re.findall(r'"songname":"(.+?)","songorig"', songListHtmlContent)
        for j in range(len(songIdList)):
            songList.append(songIdList[j] + '==' + songNameList[j])

    return songList


# 根据歌手页码开启下载
def startDownloadByPage(pageNum):
    singers = getSingerListByPageNum(pageNum)
    print('有' + str(len(singers)) + '位歌手')
    for i in range(len(singers)):
        singerId = singers[i].split('-')[0]
        singerName = singers[i].split('-')[1]
        # 创建歌手文件夹
        singerPath = music_dir_path + singerName
        if not os.path.exists(singerPath):
            os.mkdir(singerPath)

        # 循环歌单并下载
        songs = getSongListBySingerId(singerId)
        print(singerName + '有' + str(len(songs)) + '首歌')
        for j in range(len(songs)):
            songId = songs[j].split('==')[0]
            songName = songs[j].split('==')[1]
            # 判断歌曲是否已存在
            songFilePath = singerPath + '/' + singerName + ' - ' + songName + '.mp3'

            # 若发现过滤的歌曲则删除
            if re.search(song_name_filter, songName, re.I):
                if os.path.exists(songFilePath):
                    os.remove(songFilePath)
                    continue

            # 只下载文件夹下不存在以及歌单未过滤的歌曲
            if (not os.path.exists(songFilePath)) and (not re.search(song_name_filter, songName, re.I)):
                try:
                    downloadPath = 'http://ws.stream.qqmusic.qq.com/C100' + songId + '.m4a?fromtag=38'
                    download(downloadPath, singerPath, singerName + ' - ' + songName + '.mp3')
                except Exception as err:
                    print('下载歌曲出错：singerId=' + singerId + ',singerName=' + singerName + \
                          ',songId=' + songId + ',songName=' + songName)
                    print(err)


# 主方法
startDownloadByPage(1)