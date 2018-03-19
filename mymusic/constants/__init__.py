

# 音乐文件夹路径名称（下载时会在此路径下根据歌手名创建文件夹）
music_dir_path = 'Z:/音乐/'

# 歌曲名过滤正则表达式
# song_name_filter = r'\(.*Live.*\)|\(.*Demo.*\)|\(.*现场.*\)|\(.*Remix.*\)|\(.*Mix.*\)' \
#                   r'|\(.*DJ.*\)|\(.*伴奏.*\)|\(.*纯音乐.*\)|\(.*Piano.*\)|\(.*钢琴.*\)|\(.*环绕.*\)'
song_name_filter = '[\\/:*?"<>|]'

# 最小下载等待间隔（秒）
download_min_time = 10

# 最大下载等待间隔（秒）
download_max_time = 30

# =======日志设置========
log_file_name = "music_download.log"
log_fmt = "%(asctime)s - %(levelname)s - %(message)s"
log_date_fmt = "%Y-%m-%d %H:%M:%S"
# =======日志设置========
