import mymusic.utils.logger as logger
import mymusic.business.download_qq as qq


log = logger.getlogger()

def start_qq():
    log.error('QQ音乐开始')

    for i in range(1, 101):
        log.error('QQ音乐--第%s页歌手'% (i))
        qqmusic = qq.QqMusic()
        qq.QqMusic.startDownloadByPage(qqmusic, i)






start_qq()