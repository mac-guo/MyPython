import urllib.request
import os
import re
import time
import random
import ssl
import base64
from mymusic.business.download_base import DownloadBase
import mymusic.utils.logger as logger
import mymusic.constants as constants
import mymusic.service.connect_mysql as mysql
from mymusic.model.singer_info import SingerInfo
from mymusic.model.song_info import SongInfo
from mymusic.model.lyric_info import LyricInfo
import  mymusic.utils.lyric_replace as lyric_replace


log = logger.getlogger()


class QqMusic(DownloadBase):

    context = ssl._create_unverified_context()

    platform_path = "QQ Music/"

    # 下载链接qq号（目前不知道有什么用，随便填一个真实QQ号）
    url_qq_number = '349602330'

    singerListUrl = 'https://c.y.qq.com/v8/fcg-bin/v8.fcg?' + \
                    'channel=singer' + \
                    '&page=list' + \
                    '&key=all_all_all' + \
                    '&pagesize=100' + \
                    '&pagenum=%d' + \
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
                  '&singermid=%s' + \
                  '&order=listen' + \
                  '&begin=%d' + \
                  '&num=30' + \
                  '&songstatus=1'

    query_lyric_url = ''

    query_lyric_new_url = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg?' \
                          'callback=MusicJsonCallback_lrc' \
                          '&pcachetime=%s' \
                          '&songmid=%s' \
                          '&g_tk=1070532161' \
                          '&jsonpCallback=MusicJsonCallback_lrc' \
                          '&loginUin=' + url_qq_number + \
                          '&hostUin=0' \
                          '&format=jsonp' \
                          '&inCharset=utf8' \
                          '&outCharset=utf-8' \
                          '&notice=0' \
                          '&platform=yqq' \
                          '&needNewCode=0'

    downloadPath = 'http://ws.stream.qqmusic.qq.com/C100%s.m4a?fromtag=38'

    # 根据页码获取歌手列表
    def getSingerListByPageNum(self, pageNum):
        response = urllib.request.urlopen(self.singerListUrl % (pageNum), context=self.context)
        singer_list_html_content = response.read().decode(encoding="utf-8")
        singer_list = []
        singer_id_list = re.findall(r'"Fsinger_mid":"(.*?)","Fsinger_name"', singer_list_html_content)
        singer_name_list = re.findall(r'"Fsinger_name":"(.*?)","Fsinger_tag"', singer_list_html_content)
        try:
            for i in range(len(singer_id_list)):
                # 查询数据库是否已存在该歌手，不存在则添加
                singerinfo = SingerInfo(0, singer_name_list[i], 1, singer_id_list[i], (pageNum-1)*len(singer_id_list)+i+1)
                dao = mysql.MyConn()
                selectsql = "select singer_id,singer_name,platform_id,platform_code,platform_sort from singer_info where singer_name=%s and platform_id=%s and platform_code=%s"
                result = dao.select_one(selectsql, [singer_name_list[i], 1, singer_id_list[i]])
                if result is None:
                    dao.execute_trans("insert into singer_info(singer_name, platform_id, platform_code, platform_sort) values(%s, %s, %s, %s)", \
                                      [singer_name_list[i], 1, singer_id_list[i], (pageNum-1)*len(singer_id_list)+i+1])
                    idrel = dao.select_one(selectsql, [singer_name_list[i], 1, singer_id_list[i]])
                    singerinfo.singer_id = idrel[0]
                else:
                    singerinfo = SingerInfo(result[0], result[1], result[2], result[3], result[4])
                    dao.execute_trans("update singer_info set platform_sort=%s where singer_name=%s and platform_id=%s and platform_code=%s", \
                                      [(pageNum-1)*len(singer_id_list)+i+1, singer_name_list[i], 1, singer_id_list[i]])
                singer_list.append(singerinfo)
        except BaseException as err:
            log.error(u'getSingerListByPageNum error, err=%s, singerListHtmlContent=%s, singerIdList=%s, singerNameList=%s' \
                        % (err.__str__(), singer_list_html_content, singer_id_list, singer_name_list))
        return singer_list

    # 根据歌手id获取歌单列表
    def getSongListBySingerId(self, singer_info):
        print("%d----%s" % (singer_info.singer_id, singer_info.singer_name))
        # 先获取总页数
        response = urllib.request.urlopen(self.songListUrl % (singer_info.platform_code, 0), context=self.context)
        song_list_html_content = response.read().decode(encoding="utf-8")
        total_song_size = re.findall(r'"total":(\d+?)},', song_list_html_content)[0]

        # 总页数  从0开始
        total_page = int(int(total_song_size) / 30)

        # 循环每页获取歌单
        song_list = []
        for i in range(0, total_page + 1):
            response = urllib.request.urlopen(self.songListUrl % (singer_info.platform_code, i*30), context=self.context)
            song_list_html_content = response.read().decode(encoding="utf-8")
            song_id_list = re.findall(r'"strMediaMid":"(.+?)","stream"', song_list_html_content)
            song_name_list = re.findall(r'"songname":"(.+?)","songorig"', song_list_html_content)
            try:
                for j in range(len(song_id_list)):
                    # 查询数据库是否已存在该歌曲
                    dao = mysql.MyConn()
                    selectsql = "select song_id,song_name,singer_id,lyric_id,album_id,file_name,file_path,platform_id,platform_code,platform_sort,download_url" \
                                " from song_info where singer_id=%s and song_name=%s and platform_code=%s and platform_id=1"
                    result = dao.select_one(selectsql, [singer_info.singer_id, song_name_list[j], song_id_list[j]])
                    songinfo = SongInfo(0, song_name_list[j], singer_info.singer_id, None, None, None, None, 1, song_id_list[j], i*30+j+1, None)
                    if result is None:
                        dao.execute_trans("insert into song_info(song_name,singer_id,platform_id,platform_code,platform_sort) values(%s, %s, 1, %s, %s)", \
                                          [song_name_list[j], singer_info.singer_id, song_id_list[j], i*30+j+1])
                        idrel = dao.select_one(selectsql, [singer_info.singer_id, song_name_list[j], song_id_list[j]])
                        songinfo.song_id = idrel[0]
                    else:
                        songinfo = SongInfo(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9], result[10])
                        dao.execute_trans("update song_info set platform_sort=%s where singer_id=%s and song_name=%s and platform_code=%s and platform_id=1", \
                                          [i*30+j+1, singer_info.singer_id, song_name_list[j], song_id_list[j]])
                    song_list.append(songinfo)
            except BaseException as err:
                log.error(u'getSongListBySingerId error, err=%s, singerId=%s, songListHtmlContent=%s, songIdList=%s, songNameList=%s' \
                            % (err.__str__(), singer_info.platform_code, song_list_html_content, song_id_list, song_name_list))

        return song_list

    # 根据歌手页码开启下载
    def startDownloadByPage(self, pageNum):
        singer_list = self.getSingerListByPageNum(pageNum)
        print('有' + str(len(singer_list)) + '位歌手')
        log.error('有' + str(len(singer_list)) + '位歌手')

        song_list = None
        singer_id = None
        singer_name = None
        song_id = None
        song_name = None

        for i in range(len(singer_list)):
            try:
                singer_id = singer_list[i].platform_code
                singer_name = singer_list[i].singer_name
                # 创建歌手文件夹
                singer_path = constants.music_dir_path + self.platform_path + singer_name
                # if not os.path.exists(singer_path):
                #     os.mkdir(singer_path)

                # 循环歌单并下载
                song_list = self.getSongListBySingerId(singer_list[i])
                print(singer_name + '有' + str(len(song_list)) + '首歌')

                for j in range(len(song_list)):
                    try:
                        song_id = song_list[j].platform_code
                        song_name = song_list[j].song_name
                        # 判断歌曲是否已存在
                        song_file_path = singer_path + '/' + singer_name + ' - ' + song_name + '.mp3'
                        # 替换非法字符
                        singer_name = re.sub(constants.song_name_filter, '-', singer_name)
                        song_name = re.sub(constants.song_name_filter, '-', song_name)

                        # 保存歌曲下载地址及文件路径到数据库
                        dao = mysql.MyConn()
                        dao.execute_trans("update song_info set file_name=%s,file_path=%s,download_url=%s where song_id=%s", \
                                          [singer_name + ' - ' + song_name + '.mp3', song_file_path, self.downloadPath % (song_id), song_list[j].song_id])

                        # 歌词
                        self.download_lyric(song_list[j])
                        print(song_file_path)

                        # 只下载文件夹下不存在的歌曲
                        # if not os.path.exists(song_file_path):
                        #     self.download_and_save(self.downloadPath % (song_id), singer_path, singer_name + ' - ' + song_name + '.mp3')

                    except BaseException as err:
                        log.error(u'下载歌曲出错：singerId=' + singer_id + ',singerName=' + singer_name + \
                                    ',songId=' + song_id + ',songName=' + song_name + 'error=' + err.__str__())
            except BaseException as err:
                log.error(u'该歌手异常，singerId=%s，singerName=%s，error=%s' % (singer_id, singer_name, err.__str__()))
                log.error(u'singers=%s, songs=%s' % (singer_list, song_list))

    # 下载及保存歌曲
    def download_and_save(self, url, filePath, fileName):
        local = os.path.join(filePath, fileName)
        urllib.request.urlretrieve(url, local, None)
        print('下载完成：' + fileName)
        # 随机等待一定时间 10-30s
        randomNum = random.randint(constants.download_min_time, constants.download_max_time)
        print('休息' + str(randomNum) + '秒')
        print('\n')
        time.sleep(randomNum)

    # 下载歌词
    def download_lyric(self, song_info):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36 Maxthon/5.1.6.3000',
                'Referer':'https://y.qq.com/portal/player.html',
                'Accept':'*/*'
            }
            url = self.query_lyric_new_url % (int(time.time()), song_info.platform_code)

            response = urllib.request.Request(url, headers=headers)
            lyric_html_content = urllib.request.urlopen(response).read().decode(encoding="utf-8")
            lyric_base64 = re.findall(r'"lyric":"(.*?)","trans"', lyric_html_content)[0]
            lyric_str = base64.b64decode(lyric_base64).decode(encoding="utf-8")
            # 过滤歌词
            # lyricfilter = lyric_replace.lyric_filter
            # lyricfilter.append(".*" + song_info.song_name + ".*-.*")
            # lyricfilter.append(".*-.*" + song_info.song_name + ".*")
            lyric_pure = lyric_replace.get_pure_lyric_v2(lyric_str)

            # 保存
            dao = mysql.MyConn()
            selectsql = 'select lyric_id,lyric_name,lyric_content,lyric_pure,file_name,file_path,platform_id,platform_code from lyric_info ' \
                        'where lyric_name=%s and platform_id=1 and platform_code=%s'
            lyric_result = dao.select_one(selectsql, [song_info.song_name, song_info.platform_code])
            if lyric_result is None:
                dao.execute_trans("insert into lyric_info(lyric_name,lyric_content, lyric_pure,platform_id,platform_code) " \
                                  "values(%s, %s, %s, %s, %s)", [song_info.song_name, lyric_str, lyric_pure, 1, song_info.platform_code])
                lyric_result = dao.select_one(selectsql, [song_info.song_name, song_info.platform_code])
            else:
                dao.execute_trans("update lyric_info set lyric_content=%s,lyric_pure=%s where lyric_name=%s and platform_id=1 and platform_code=%s", \
                                  [lyric_str, lyric_pure, song_info.song_name, song_info.platform_code])

            # 更新歌曲表歌词编号
            dao.execute_trans("update song_info set lyric_id=%s where singer_id=%s and song_name=%s and platform_code=%s and platform_id=1", \
                              [lyric_result[0], song_info.singer_id, song_info.song_name, song_info.platform_code])
        except BaseException as err:
            log.error(u'歌词下载失败，singerId=%s，singerName=%s，error=%s' % (song_info.platform_code, song_info.song_name, err.__str__()))















