#!/usr/bin/env python3

# B站评论爬虫工具
#  + 爬取前两层评论信息
#  + 因为没找到更新的API:深层评论暂时爬不出来，所以评论总数和ｂ站显示有差距

import re
import os,sys,csv
import requests
from lxml import etree
import PROTOCAL
from ESSENTIAL import bilibili_reply

# 回复信息：暂未写入
SAVE_REPLY = '0'

def _read_reply_member(reply):
    _member = reply['member']
    member = {'vip':_member['vip']['vipStatus'],'sex':_member['sex'],'rank':_member['rank'], \
            'level':_member['level_info']['current_level'],'uname':_member['uname'], \
            'official_verify':_member['official_verify']}
    return member


def _read_reply_page(topList, reply_obj, write_port, mode="COMPACT"):
    # safety lock
    if not topList:
        return

    for reply in topList:
        # 每条评论信息
        message = reply['content']['message']
        meta = {'rpid':reply['rpid'],'ctime':reply['ctime'],'floor':reply['floor'], \
                'like':reply['like'],'parent':['parent']}

        if mode == "COMPACT":
            member = {'vip':'','sex':'','rank':'','level':'','uname':'','official_verify':''}
        elif mode == "FULL":
            member = _read_reply_member(reply)

        # 每条评论最终结果
        reply_obj.addreply({'message':message, 'meta':meta, 'member':member})
        print(message)
        write_port.writerow([message,meta['rpid'],meta['like'],member['uname']])

        _sublist = reply['replies']
        if _sublist:
            _read_reply_page(_sublist,reply_obj,write_port,mode)


def spider_reply(uri):
    print("爬取评论区")
    print("--------------------------------------------------------------")
    print("评论排序？(输入未规定数字或不输入数字则为时间回复顺序)")
    print("1: 时间倒叙2: 热度排序")
    choice = input("请输入你的选择（数字）:")
    if (choice == '2'):
        nohot = '0'
    else:
        nohot = '1'
    print("现在: %s" % '时间倒叙' if nohot == '1' else '热度排序')

    print("--------------------------------------------------------------")
    print("数据模式？(输入未规定数字或不输入数字则紧凑)")
    print("1: 紧凑（无发言者信息）2: 完整")
    choice = input("请输入你的选择（数字）:")
    if (choice != '1'):
        mode = 'FULL'
    else:
        mode = 'COMPACT'

    # 查找aid
    try:
        r = requests.get(uri)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    html = etree.HTML(r.text)
    aidlocator = html.xpath('//script[@language="javascript"]')[-1].text
    aid = re.search(r'aid=\'(.*)\', typeid', aidlocator).group(1)
    vtitle = html.xpath('//div[@class="v-title"]/h1/@title')[0]

    # 建立评论解析地址
    try:
        rplist_url = PROTOCAL.Bilibili_API['replyList'] % dict(_aid=str(aid))
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    r = requests.get(rplist_url)
    rplist_text = r.json()

    num = rplist_text['pages']
    owner_mid = rplist_text['owner']

    f = open(vtitle + '_reply' + '.csv',"w")
    port_csv = csv.writer(f)
    port_csv.writerow(['message','rpid','like','uname'])

    # 结果储存
    reply_obj = bilibili_reply(url=uri, title=vtitle)

    # 逐步解析每页评论
    for i in range(1,num+1):
        try:
            rppage_url = PROTOCAL.scheme + (PROTOCAL.Bilibili_API['reply'] % dict(_aid=str(aid),_pn=str(i),_nohot=str(nohot)))
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

        page_data = requests.get(rppage_url).json()['data']

        # 递归单页
        _read_reply_page(page_data['replies'], reply_obj, port_csv,mode=mode)

    f.close()


    return reply_obj


if __name__ == '__main__':
    uri = input("请输入解析地址:")
    print("开始解析： %s" % uri)
    spider_reply(uri)
