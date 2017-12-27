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

try:
    import re,os,csv
    import requests
    from lxml import etree
    from ESSENTIAL import bilibili_video
    import PROTOCAL
except ImportError as e:
    print(e)

SAVE_IMAGE = '0'
SAVE_CSV = '1'
SAVE_REPLY = '0'

def spider_video(url):

    try:
        r = requests.get(url, headers=PROTOCAL.header)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    html = etree.HTML(r.text)

    # 标题
    title = html.xpath('//div[@class="v-title"]/h1/@title')[0]

    if title:

        # 视频id
        aidlocator = html.xpath('//script[@language="javascript"]')[-1].text
        aid = re.search(r'aid=\'(.*)\', typeid', aidlocator).group(1)

        # 上传时间
        uploadtime = html.xpath('//meta[@itemprop="uploadDate"]/@content')[0]

        # 分类信息
        timeinfo = html.xpath('//div[@class="tminfo"]/span/a')
        time_log = []
        for logx in timeinfo:
            time_log.append(logx.text)

        # UP主信息
        up = html.xpath('//div[@class="usname"]/a')[0]
        mid = html.xpath('//div[@class="usname"]/a/@mid')[0]
        upspace = "https:" + html.xpath('//div[@class="usname"]/a/@href')[0]

        # 标签

        # 视频简介
        intro_text = html.xpath('//div[@class="v_desc report-scroll-module report-wrap-module"]')[0].text

        # cids &　分P
        cids = []
        cid_urls = []
        videos = html.xpath('//option')

        if videos:
            for video in videos:
                cids.append(video.xpath('.//@cid')[0])
                cid_urls.append( PROTOCAL.scheme + PROTOCAL.web['Bilibili'] + video.xpath('.//@value')[0])
        else:
            cidlocator = html.xpath('//script[@type="text/javascript" and contains(., "EmbedPlayer")]')[0].text
            cids.append(re.search('cid=(.*)&aid',cidlocator).group(1))
            cid_urls.append(PROTOCAL.scheme + PROTOCAL.web['Bilibili'] + '/video/' + str(aid))

        # 视频信息
        info_url = PROTOCAL.scheme + PROTOCAL.Bilibili_API['info'] % dict(_cid=str(cids[0]),_aid=str(aid))
        try:
            video_info = requests.get(info_url)
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

        # 档案信息
        try:
            archive_url = PROTOCAL.scheme + PROTOCAL.Bilibili_API['archive'] % dict(_aid=str(aid))
            archive = requests.get(archive_url, headers=PROTOCAL.header).json()['data']
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

        favorite = str(archive['favorite'])
        danmaku = str(archive['danmaku'])
        coin = str(archive['coin'])
        view = str(archive['view'])
        share = str(archive['share'])
        reply = str(archive['reply'])
        click = str(re.search('<click>(.*)</click>',video_info.text).group(1))
        duration = str(re.search('<duration>(.*)</duration>',video_info.text).group(1))

        # 回复信息
        # 请用GetReply.py爬取回复数据

    else:
        raise Exception ("Error 404: " + url)

    # 储存爬虫结果
    meta_info = {'url':url,'title':title,'aid':aid,'cid':cids[0],'uploadtime':uploadtime,'duration':duration, 'category':time_log}
    play_info ={'view':view,'click':click,'favorite':favorite,'coin':coin,'danmaku':danmaku,'reply':reply,'share':share}
    up_info = {'up':up,'mid':mid, 'upspace':upspace}
    text_info = {'intro':intro_text}

    video_obj = bilibili_video({**meta_info, **play_info, **up_info, **text_info})

    return video_obj

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
        r = requests.get("http:" + page_url, headers = PROTOCAL.header)
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
    page = PROTOCAL.Bilibili_API['search'] % dict(_keyword=keyword)
    order = "&order=totalrank"
    #关于order的解释:        -
    #   totalrank 综合排序   -
    #   click 最多点击       -
    #   pubdate 最新发布     -
    #   dm 最多弹幕          -
    #   stow 最多收藏        -

    # path = "G:\\bilibilispider\\" + keyword #把G:\\bilibilispider\\ 改成 你所要存储的文件夹
    path = os.getcwd() + '/GetCover/' + keyword

    try:
        os.stat(path)
    except:
        os.makedirs(path)

    print("--------------------------------------------------------------")
    print("搜索结果将以何种方式显示？(输入未规定数字或不输入数字则为综合排序)")
    print("1: 综合排序 2:最多点击 3:最新发布 4:最多弹幕 5:最多收藏")
    print("--------------------------------------------------------------")
    choice = input("请输入你的选择（数字）:")

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
    print("现在" + order)

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

    r = requests.get(page + str(1) + order, headers = PROTOCAL.header)
    index_html = etree.HTML(r.text)
    page_upper = index_html.xpath('//body[@class="report-wrap-module old-ver"]')[0]
    page_upper_int = int(page_upper.xpath('.//@data-num_pages')[0]) + 1
    print("循环上界：" + str(page_upper_int))
    input("输入任意键开始...")

    if (SAVE_IMAGE == '1'):
        make_pageFile(path, page_upper_int, order)

    if (SAVE_CSV == '1'):
        f = open(path + '/' + keyword + '_' + order[7:] + '.csv',"w")
        port_csv = csv.writer(f)
        port_csv.writerow(bilibili_video().writekey())

    if (SAVE_CSV != '1' and SAVE_IMAGE != '1'):
        print('保存简单搜索结果至： ' + path)
        path = path + '_' + order[7:] + '_链接.csv'
        f = open(path,'w')
        port_csv = csv.writer(f)


    for i in range(1, page_upper_int):
        r = requests.get(page + str(i) + order,headers = PROTOCAL.header)
        html = etree.HTML(r.text)
        video_list = html.xpath('//li[@class="video matrix "]')
        for li in video_list:
            print("----------------------------")
            print(li.xpath('.//a/@title')[0])
            video_r = requests.get("https:" + li.xpath('.//a/@href')[0], headers = PROTOCAL.header)
            video_html = etree.HTML(video_r.text)

            if (SAVE_IMAGE == '1'):
                print("开始爬取图片")
                img_src = video_html.xpath('//img[@class="cover_image"]/@src')[0]
                print (img_src)
                save(path,img_src,li.xpath('.//a/@title')[0],i,order)

            if (SAVE_CSV == '1'):
                print("开始爬取数据")
                info = spider_video("https:" + re.search(r'(.*)\?',li.xpath('.//a/@href')[0]).group(1))
                port_csv.writerow(info.writevalue())

            if (SAVE_CSV != '1' and SAVE_IMAGE != '1'):
                port_csv.writerow([li.xpath('.//a/@title')[0],"https:" + re.search(r'(.*)\?',li.xpath('.//a/@href')[0]).group(1)])

            print("----------------------------")
            # input("任意键继续下一项...")
        print("第" + str(i) + "页爬取完毕")
        print("----------------------------")

    if (SAVE_CSV == '1'):
        f.close()
