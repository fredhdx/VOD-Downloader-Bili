#!/usr/bin/env python3

# B站爬虫工具
#    + 视频信息
#    + 首页图片存储
#    + 更新时间 - 2017.12.22
#    + Python version: 3.6.3
#         + 参考：airingursb/bilibili-video
#         + 参考2：http://www.cnblogs.com/liuliliuli2017/p/6746433.html
#         + 参考3：airingursb/bilibili-danmu
#         + 参考4：airingursb/bilibili-user

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

PROTOCAL = "https://"
Bilibili = "www.bilibili.com"
MODE = ""

SAVE_IMAGE = '0'
SAVE_CSV = '1'

def spider(url):

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

        # 分类信息
        timeinfo = soup.find('div', class_="tminfo")
        time_log = []
        for logx in timeinfo.find_all('span'):
            time_log.append(logx.a.text)

        # UP主信息
        up = soup.find('div', class_="usname").a.text
        mid = soup.find('div', class_="usname").a['mid']
        upspace = "https:" + soup.find('div', class_="usname").a['href']

        # 标签

        # 视频简介
        intro_text = soup.find('div', class_="v_desc report-scroll-module report-wrap-module").text

        # cids &　分P
        cids = []
        cid_urls = []
        videos = soup.find_all('option')

        if videos:
            for video in videos:
                cids.append(video['cid'])
                cid_urls.append( PROTOCAL + Bilibili + video['value'])
        else:
            cidlocator = soup.find('script',{"type":"text/javascript"},text=re.compile('EmbedPlayer')).text
            cids.append(re.search('cid=(.*)&aid',cidlocator).group(1))
            cid_urls.append(PROTOCAL + Bilibili + '/video/' + str(aid))

        # 视频信息：已被移植json
        info_url = PROTOCAL + "interface.bilibili.com/player?id=cid:" + str(cids[0]) + "&aid=" + aid
        try:
            video_info = requests.get(info_url)
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

        try:
            json_url = PROTOCAL + "api.bilibili.com/archive_stat/stat?aid=" + aid
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
        json_url2 = PROTOCAL + "api.bilibili.com/x/reply?jsonp=jsonp&type=1&sort=0&pn=1&nohot=1&oid=" + aid

    else:
        raise Exception ("Error 404: " + url)

    # 储存爬虫结果
    meta_info = {'url':url,'title':title,'aid':int(aid),'cid':int(cids[0]),'uploadtime':uploadtime,'duration':duration, 'category':time_log}
    play_info ={'view':view,'click':click,'favorite':favorite,'coin':coin,'danmaku':danmaku,'reply':reply,'share':share}
    up_info = {'up':up,'mid':mid, 'upspace':upspace}
    text_info = {'intro':intro_text}
    result = bilibili_video({**meta_info, **play_info, **up_info, **text_info})

    return result

def make_pageFile(path,page_num,order):
    #具体实施的方法：
    #1 先创建一个(keyword)&order=() 格式的文件夹.
    #2 在这个文件夹下以逐渐递增的数字创建文件夹。文件夹的数量与搜索结果页的页数相等。
    #3 存储图片。 将第一页的图片存储到第一页下，以此类推。

    # order = "&order=totalrank"
    order = order[7:]

    if not os.path.exists(path + '/' + order):
        print('making dir: ' + order)
        os.makedirs(path + '/' + order )

    for num in range(1,page_num):
        if not os.path.exists(path + "/" + order + "/" +str(num)):
            os.makedirs(path + "/" + order + "/" +str(num))

def save(path,page_url,title,page_num,order):
    order = order[7:]
    if not os.path.exists(path + "/" + order):
        os.makedirs(path + "/" + order)
    try:
        r = requests.get("http:" + page_url, headers = UA)
        path = path + "/" + order +"/" + str(page_num) + "/"+ title + "." +page_url.split('.')[-1]
        if not os.path.exists(path):
            f = open(path, "wb")
            f.write(r.content)
            f.close()
            print("【-保存于-】:"+path)
        else:
            print("【-已存在-】:"+path)
    except:
        print("【【获取失败】】："+title)

if __name__ == '__main__':
    count = 1
    keyword = input('输入关键词(逻辑符: " "与 "+"或 "-"非)：')
    page = "https://search.bilibili.com/all?keyword=" + keyword + "&page="
    order = "&order=totalrank"
    #关于order的解释:        -
    #   totalrank 综合排序   -
    #   click 最多点击       -
    #   pubdate 最新发布     -
    #   dm 最多弹幕          -
    #   stow 最多收藏        -

    # path = "G:\\bilibilispider\\" + keyword #把G:\\bilibilispider\\ 改成 你所要存储的文件夹
    path = os.getcwd() + '/' + keyword
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

    q = requests.get(page + str(1) + order, headers = UA)
    Soup_q = BeautifulSoup(q.text, 'html5lib')
    page_upper = Soup_q.find('body', class_="report-wrap-module old-ver")
    page_upper_int = int(page_upper['data-num_pages']) + 1
    print("循环上界：" + str(page_upper_int))
    input("输入任意键开始...")

    if (SAVE_IMAGE == '1'):
        make_pageFile(path, page_upper_int, order)

    if (SAVE_CSV == '1'):
        f = open(keyword + '_' + order[7:] + '.csv',"w")
        port_csv = csv.writer(f)
        port_csv.writerow(bilibili_video().writekey())

    if (SAVE_CSV != '1' and SAVE_IMAGE != '1'):
        print('保存简单搜索结果至： ' + path)
        path = path + '_' + order[7:] + '_链接.csv'
        f = open(path,'w')
        port_csv = csv.writer(f)


    for i in range(1, page_upper_int):
        r = requests.get(page + str(i) + order,headers = UA)
        Soup = BeautifulSoup(r.text,'html5lib')
        all_li = Soup.find_all('li', class_ = "video matrix " )
        for li in all_li:
            print("----------------------------")
            print(li.a['title'])
            video_html = requests.get("https:" + li.a['href'], headers = UA)
            video_soup = BeautifulSoup(video_html.text,'html5lib')

            if (SAVE_IMAGE == '1'):
                print("开始爬去图片")
                img_src = video_soup.find('img')
                print (img_src['src'])
                save(path,img_src['src'],li.a['title'],i,order)

            if (SAVE_CSV == '1'):
                print("开始爬取数据")
                info = spider("https:" + re.search(r'(.*)\?',li.a['href']).group(1))
                port_csv.writerow(info.writevalue())

            if (SAVE_CSV != '1' and SAVE_IMAGE != '1'):
                port_csv.writerow([li.a['title'],"https:" + re.search(r'(.*)\?',li.a['href']).group(1)])

            print("----------------------------")
            # input("任意键继续下一项...")
        print("第" + str(i) + "页爬取完毕")
        print("----------------------------")

    if (SAVE_CSV == '1'):
        f.close()
