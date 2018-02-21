#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
# B站爬虫工具
#    + 视频信息
#    + 首页图片存储
#    + 更新时间 - 2017.12.22
#    + Python version: 3.6.3
#         + 参考：airingursb/bilibili-video
#         + 参考2：http://www.cnblogs.com/liuliliuli2017/p/6746433.html
#         + 参考3：airingursb/bilibili-danmu
#         + 参考4：airingursb/bilibili-user
'''

import requests
import os,sys,re
import time
import csv
from bs4 import BeautifulSoup
from model import bilibili_video

UA = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
    AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/35.0.1916.114 Safari/537.36',
    'Cookie': 'AspxAutoDetectCookieSupport=1'
}

PROTOCAL_ARCHIVE = "https://"
PROTOCAL_IMAGE = "https:"
Bilibili = "www.bilibili.com"
SEARCH_API = "https://search.bilibili.com/api/search?search_type=all&keyword="
SPACE_API = "https://space.bilibili.com/"
MODE = ""

SAVE_IMAGE = '0'
SAVE_CSV = '1'

def remove_nbws(text):
    """ remove unwanted unicode punctuation: zwsp, nbws, \t, \r, \r.
    """

    # ZWSP: Zero width space
    text = text.replace(u'\u200B', '')
    # NBWS: Non-breaking space
    text = text.replace(u'\xa0', ' ')
    # HalfWidth fullstop
    text = text.replace(u'\uff61', '')
    # Bullet
    text = text.replace(u'\u2022', '')
    # White space
    text = text.replace(u'\t', ' ').replace(u'\r', ' ')

    # General Punctuation
    gpc_pattern = re.compile(r'[\u2000-\u206F]')
    text = gpc_pattern.sub('', text)

    # Mathematical Operator
    mop_pattern = re.compile(r'[\u2200-\u22FF]')
    text = mop_pattern.sub('', text)

    # Combining Diacritical Marks
    dcm_pattern = re.compile(r'[\u0300-\u036F]')
    text = dcm_pattern.sub('', text)

    # Hangul Syllable
    hangul_pattern = re.compile(r'[\uac00-\ud7af]')
    text = hangul_pattern.sub('',text)

    lsp_pattern = re.compile(r'[\x80-\xFF]')
    text = lsp_pattern.sub('', text)

    return text

def spider(url):
    ''' 解析单个视频链接
    '''
    try:
        html = requests.get(url, headers=UA)
        soup = BeautifulSoup(html.text,'html5lib')
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    # 标题
    title = soup.find('div', class_="v-title").h1['title'] # 标题

    if title:

        # 视频id
        aidlocator = soup.findAll('script', {'language':"javascript"})[-1]
        aid = re.search(r'aid=\'(.*)\', typeid', aidlocator.text).group(1)

        # 上传时间
        uploadtime = soup.find('meta',attrs={'itemprop':"uploadDate"})['content']

        # 封面图片
        pic_url = PROTOCAL_IMAGE + soup.find('img')['src']

        # 分类信息
        timeinfo = soup.find('div', class_="tminfo")
        time_log = []
        for logx in timeinfo.find_all('span'):
            time_log.append(logx.a.text)

        # UP主信息
        up = remove_nbws(soup.find('div', class_="usname").a.text)
        mid = soup.find('div', class_="usname").a['mid']
        upspace = "https:" + soup.find('div', class_="usname").a['href']

        # 标签

        # 视频简介
        intro_text = remove_nbws(soup.find('div', class_="v_desc report-scroll-module report-wrap-module").text)

        # cids &　分P
        cids = []
        cid_urls = []
        videos = soup.find_all('option')

        if videos:
            for video in videos:
                cids.append(video['cid'])
                cid_urls.append( PROTOCAL_ARCHIVE + Bilibili + video['value'])
        else:
            cidlocator = soup.find('script',{"type":"text/javascript"},text=re.compile('EmbedPlayer')).text
            cids.append(re.search('cid=(.*)&aid',cidlocator).group(1))
            cid_urls.append(PROTOCAL_ARCHIVE + Bilibili + '/video/' + str(aid))

        # 视频信息：已被移植json
        info_url = PROTOCAL_ARCHIVE + "interface.bilibili.com/player?id=cid:" + str(cids[0]) + "&aid=" + aid
        try:
            video_info = requests.get(info_url)
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

        try:
            json_url = PROTOCAL_ARCHIVE + "api.bilibili.com/archive_stat/stat?aid=" + aid
            json = requests.get(json_url, headers=UA).json()['data']
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

        favorite = json['favorite']
        danmaku = json['danmaku']
        coin = json['coin']
        view = json['view']
        share = json['share']
        reply = json['reply']
        click = re.search('<click>(.*)</click>',video_info.text).group(1)
        duration = re.search('<duration>(.*)</duration>',video_info.text).group(1)

        # another json api 有一些额外信息
        # json_url2 = PROTOCAL_ARCHIVE + "api.bilibili.com/x/reply?jsonp=jsonp&type=1&sort=0&pn=1&nohot=1&oid=" + aid

    else:
        raise Exception ("Error 404: " + url)

    # 储存爬虫结果
    meta_info = {'title':title,'aid':aid,'cid':cids[0],'uploadtime':uploadtime,
                 'duration':duration, 'category':time_log, 'description':intro_text}
    play_info ={'view':view,'click':click,'favorite':favorite,'coin':coin,'danmaku':danmaku,'reply':reply,'share':share}
    up_info = {'author':up,'mid':mid, 'upspace':upspace}
    urls_info = {'vurl': url, 'picurl': pic_url}
    result = bilibili_video({**meta_info, **play_info, **up_info, **urls_info})

    return result

def make_pageFile(path,page_num,order):
    #具体实施的方法：
    #1 先创建一个path/keyword/order/格式的文件夹.
    #2 在这个文件夹下以逐渐递增的数字创建文件夹。文件夹的数量与搜索结果页的页数相等 /1。
    #3 存储图片。 将第一页的图片存储到第一页下，以此类推。

    # order = "&order=totalrank"
    order = order[7:]
    path = path + os.path.sep + order

    if not os.path.exists(path):
        print('making dir: ' + order)
        os.makedirs(path)

    for num in range(1,page_num + 1):
        if not os.path.exists(path + os.path.sep + str(num)):
            os.makedirs(path + os.path.sep + str(num))

def save(path, page_url, title):

    if not os.path.exists(path):
        os.makedirs(path)
    try:
        r = requests.get(PROTOCAL_IMAGE + page_url, headers = UA)
        path = path + os.path.sep + title + "." + page_url.split('.')[-1]
        if not os.path.exists(path):
            f = open(path, "wb")
            f.write(r.content)
            f.close()
            print("【-保存于-】:" + path)
        else:
            print("【-已存在-】:" + path)
    except:
        print("【【获取失败】】：" + title)

if __name__ == '__main__':
    count = 1
    keyword = input('输入关键词(逻辑符: " "与 "+"或 "-"非)：')
    page_api = SEARCH_API + keyword + "&page="
    order = "&order=totalrank"
    duration = "&duration=0"
    tids = "&tids=0"
    #关于order的解释:        -
    #   totalrank 综合排序   -
    #   click 最多点击       -
    #   pubdate 最新发布     -
    #   dm 最多弹幕          -
    #   stow 最多收藏        -
    #关于其它的option: duration:时长， tid:分区
    # 关于时长：&duration=0,1,2,3,4: 全部，10分一下，10-30，30-60，60以上
    # 关于分区：&tids=0,1,2,3,.....:全部，动画，番剧等

    # path = "G:\\bilibilispider\\" + keyword #把G:\\bilibilispider\\ 改成 你所要存储的文件夹
    path = os.getcwd() + os.path.sep + "result" + os.path.sep + keyword
    if not os.path.exists(path):
        os.makedirs(path)

    print("--------------------------------------------------------------")
    print("搜索结果将以何种方式显示？(输入未规定数字或不输入数字则为综合排序)")
    print("1: 综合排序 2:最多点击 3:最新发布 4:最多弹幕 5:最多收藏")
    print("--------------------------------------------------------------")
    choice = input("请输入你的选择（数字）:")
    print("现在" + order)

    if(choice == '1'):
        order = "&order=totalrank"
    elif(choice == '2'):
        order = "&order=click"
    elif(choice == '3'):
        order = "&order=pubdate"
    elif(choice == '4'):
        order = "&order=dm"
    elif(choice == '5'):
        order = "&order=stow"

    print("--------------------------------------------------------------")
    print("是否储存封面图片?(默认：否)")
    print("1: 是 2:否")
    print("--------------------------------------------------------------")
    choice = input("请输入你的选择（数字）:")

    if (choice == '1'):
        SAVE_IMAGE = '1'
        print("将储存封面图片")
    else:
        SAVE_IMAGE = '0'

    print("--------------------------------------------------------------")
    print("是否储存爬虫结果(.csv)?(默认：是)")
    print("1: 是 2:否")
    print("--------------------------------------------------------------")
    choice = input("请输入你的选择（数字）:")

    if (choice == '2'):
        SAVE_CSV = '0'
    else:
        SAVE_CSV = '1'
        print("爬虫结果将储存")

    page_url = page_api + str(1) + order + duration + tids
    # example: https://search.bilibili.com/api/search?search_type=all&keyword=哇&order=pubdate&duration=0&page=3&tids=0

    try:
        q = requests.get(page_url, headers = UA)
        status_code = q.status_code
    except Exception as e:
        print(e)
        sys.exit(1)

    if status_code != 200:
        print("解析: %s出错" % page_url)
        print("status_code: %d" % status_code)
        sys.exit(1)

    content_json = q.json()

    # page info
    numResults = int(content_json['pageinfo']['video']['numResults'])
    numPages = int(content_json['pageinfo']['video']['pages'])

    print("循环上界：" + str(numPages))
    print("共%d项结果" % numResults)
    input("输入任意键开始...")

    if (SAVE_IMAGE == '1'):
        make_pageFile(path, numPages, order)

    if (SAVE_CSV == '1'):
        filename = keyword + '_' + order[7:] + '.csv'
        f = open(path + os.path.sep + filename, "w", encoding='utf-8')
        port_csv = csv.writer(f)
        f.write('\ufeff')
        port_csv.writerow(bilibili_video().writestatkey())

    if (SAVE_CSV != '1' and SAVE_IMAGE != '1'):
        filename = keyword + '_' + order[7:] + '.csv'
        print('保存简单搜索结果至： ' + filename)
        f = open(path + os.path.sep + filename, 'w', encoding='utf-8')
        port_csv = csv.writer(f)
        f.write('\ufeff')


    for i in range(1, numPages + 1):
        page_url = page_api + str(i) + order + duration + tids
        try:
            r = requests.get(page_url, headers = UA)
            status_code = r.status_code
        except Exception as e:
            print(e)
            sys.exit(1)

        if status_code != 200:
            print("解析第%d页出现问题 status_code:%d" % {i, status_code})
            sys.exit(1)

        content_json = r.json()
        for j in range(1, len(content_json['result']['video']) + 1):

            # 获取每个视频数据
            item_json = content_json['result']['video'][j-1]


            # url title aid cid uploadtime duration category view click favorite coin danmaku reply share up mid upspace intro

            # meta
            title = remove_nbws(item_json['title'].replace('<em class=\"keyword\">','').replace('</em>',''))
            aid = str(item_json['id']) # 视频ID
            # cid: cid需要解析每一个视频链接获得，因为暂时没用，所以先不爬取
            video_url = item_json['arcurl'] # 视频地址
            pic_url = PROTOCAL_IMAGE + item_json['pic'] # 封面地址

            pubdate = int(item_json['pubdate']) # 和时间有关系，但不懂怎么解析，可以用于排序
            senddate = int(item_json['senddate'])
            duration = str(item_json['duration']) # 格式 22:30
            # uploadtime: 同cid

            category = item_json['typename'] # 分类
            tag = item_json['tag'] # 标签

            description = remove_nbws(item_json['description']) # 简介

            author = item_json['author'] # 作者
            mid = str(item_json['mid']) # 作者ID
            upspace = SPACE_API + str(mid) # 作者空间

            try:
                archive_url = PROTOCAL_ARCHIVE + "api.bilibili.com/archive_stat/stat?aid=" + aid
                archive_json = requests.get(archive_url, headers=UA).json()['data']
            except requests.exceptions.RequestException as e:
                print(e)
                sys.exit(1)


            # statistics
            view = int(item_json['play']) # 播放数
            favorite = int(item_json['favorites']) # 收藏
            danmaku = int(item_json['video_review']) # 弹幕
            reply = int(item_json['review']) # 评论
            share = int(archive_json['share']) # 分享
            coin = int(archive_json['coin']) # 投币


            meta_info = {'title':title, 'aid':aid, 'pubdate':pubdate, 'senddate':senddate,
                         'duration':duration, 'category':category, 'tag':tag, 'description':description}
            play_info ={'view':view, 'favorite':favorite, 'coin':coin, 'danmaku':danmaku, 'reply':reply, 'share':share}
            up_info = {'author':author, 'mid':mid, 'upspace':upspace}
            urls_info = {'vurl': video_url, 'picurl': pic_url}
            result = bilibili_video({**meta_info, **play_info, **up_info, **urls_info})


            print("----------------------------")
            print(title)

            if (SAVE_IMAGE == '1'):
                print("开始爬取图片")
                image_path = path + os.path.sep + order + os.path.sep + str(i)
                save(image_path, pic_url, title)

            if (SAVE_CSV == '1'):
                port_csv.writerow(result.writestat())

            if (SAVE_CSV != '1' and SAVE_IMAGE != '1'):
                port_csv.writerow([title, video_url])

            print("----------------------------")
            # input("任意键继续下一项...")
        print("第" + str(i) + "/" + str(numPages) + "页爬取完毕")
        print("----------------------------")

    if (SAVE_CSV == '1'):
        f.close()
