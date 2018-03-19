import re
import time

lyric_filter = ['词:', '词：', '曲:', '曲：', '编曲:', '编曲：', '制作人:', '制作人：', \
                '合声:', '合声：', '录音师:', '录音师：', '混音师:', '混音师：', '母带处理工程师:', '母带处理工程师：', \
                '混音室:', '混音室：', '音乐总监:', '音乐总监：', 'PGM:', 'PGM：', '键盘:', '键盘：', \
                '吉他手:', '吉他手：', '贝斯手:', '贝斯手：', '鼓手:', '鼓手：', \
                '打击乐:', '打击乐：', '萨克斯:', '萨克斯：', '小号:', '小号：', \
                '长号:', '长号：', '和声:', '和声：', '弦乐:', '弦乐：', \
                '声乐指导:', '声乐指导：', '录音助理:', '录音助理：', '大提琴:', '大提琴：', \
                '鼓:', '鼓：', '吉他:', '吉他：', '女声:', '女声：', \
                '贝斯:', '贝斯：', '乐队总监:', '乐队总监：', '乐队队长:', '乐队队长：', \
                '乐队:', '乐队：', '电脑工程:', '电脑工程：', '音乐统筹:', '音乐统筹：', \
                '鼓录音:', '鼓录音：', '演奏乐队:', '演奏乐队：', '钢琴:', '钢琴：', \
                '录音:', '录音：', '混音:', '混音：', '母带:', '母带：']

def get_pure_lyric(lyric_content, filter_args):
    start = int(time.time()*1000)
    lyric_content = re.sub(r'\[.+\]', "", lyric_content)

    read_file = open('lyric_temp.txt', 'w', encoding="utf-8")
    read_file.write(lyric_content)
    read_file.close()

    write_file = open('lyric_temp.txt', 'r', encoding="utf-8")
    lines = write_file.readlines()
    lyric_pure = ''
    is_first = True
    for i in range(1, len(lines)):
        line = lines[i]
        if len(line) != 0 and line != '\n' and is_filter_words(line, filter_args) is False:
            if is_first is False:
                lyric_pure += line.replace(" ", "\n")
            else:
                is_first = False
    write_file.close()
    end = int(time.time()*1000)
    print("耗时：" + str(end - start))
    return lyric_pure


def is_filter_words(target_str, filters):
    for i in range(len(filters)):
        if re.search(filters[i], target_str):
            return True
    return False


def get_pure_lyric_v2(lyric_content):
    lyric_content = re.sub(r'\[.+\]', "", lyric_content)

    read_file = open('lyric_temp.txt', 'w', encoding="utf-8")
    read_file.write(lyric_content)
    read_file.close()

    write_file = open('lyric_temp.txt', 'r', encoding="utf-8")
    lines = write_file.readlines()
    lyric_pure = ''
    is_first = True
    for i in range(1, len(lines)):
        line = lines[i]
        idx1 = line.find(":")
        idx2 = line.find("：")
        idx = idx1 if idx1 > idx2 else idx2
        if idx > -1:
            line = line[idx + 1: len(line)].lstrip()
        if len(line) != 0 and line != '\n':
            if is_first is False:
                lyric_pure += line.replace(" ", "\n")
            else:
                is_first = False
    write_file.close()
    return lyric_pure

