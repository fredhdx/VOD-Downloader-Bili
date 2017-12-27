#!/usr/bin/env python3
"""doc
B站爬虫工具：class definition

+ bilibili_video: __init__(info={}) 单个视频对象
        + self.meta, self.up, self.up, self.text
+ bilibili_reply: addreply(newreply={}) 单个视频对象
        + self.title, self.replyList=[{'message','meta','member'}]
"""

import re
import os,sys
import requests
from lxml import etree
import PROTOCAL

# 回复信息：暂未写入
SAVE_REPLY = '0'

class bilibili_video:
    "store bilibili video info (single)"
    "信息分别储存于: meta和play两个字典里"
    "methods: update(ditionary), write(list of key values)"

    def __init__(self, args={}):
        self.meta = {'url':'','title':'','aid':'','cid':'','uploadtime':'','duration':'','category':''}
        self.play = {'view':'','click':'','favorite':'','coin':'','danmaku':'','reply':'','share':''}
        self.up = {'up':'','mid':'', 'upspace':''}
        self.text = {'intro':''}

        if bool(args):
            self.update(args)

    # args is dictionary
    def update(self, args):
        if not args:
            print("Error: bilibili_video.assign(args): empty args")
            sys.exit(1)
        else:
            for k_args in args:
                if k_args in self.meta:
                    self.meta[k_args] = args[k_args]
                elif k_args in self.play:
                    self.play[k_args] = args[k_args]
                elif k_args in self.up:
                    self.up[k_args] = args[k_args]
                elif k_args in self.text:
                    self.text[k_args] = args[k_args]
                else:
                    print("Warning: key %s not found in bilibili_video" % k_args)

    # kargs should be list of keys
    def write(self,kargs=[]):
        if not kargs:
            outline = list(self.meta.items()) + list(self.play.items()) + list(self.up.items()) + list(self.text.items())
        else:
            outline = []
            for key in kargs:
                if key in self.meta:
                    outline.append('(' + key + ',' + str(self.meta[key]) + ')')
                elif key in self.play:
                    outline.append('(' + key + ',' + str(self.play[key]) + ')')
                elif key in self.up:
                    outline.append('(' + key + ',' + str(self.up[key]) + ')')
                elif key in self.text:
                    outline.append('(' + key + ',' + str(self.text[key]) + ')')
                else:
                    print("Warning: key %s not found in bilibili_video" % key)

        print(outline)

    def writevalue(self):
        row = list(self.meta.values()) + list(self.play.values()) + list(self.up.values()) + list(self.text.values())
        return row

    def writekey(self):
        row = list(self.meta.keys()) + list(self.play.keys()) + list(self.up.keys()) + list(self.text.keys())
        return row


class bilibili_reply:
    "store bilibili video reply info (per reply)"
    "message = reply['content']['message']"
    "meta = {'rpid':reply['rpid'],'ctime':reply['ctime'],'floor':reply['floor'],"
    "        'like':reply['like'],'parent':['parent']}"
    "member = _read_reply_member(reply)"

    def __init__(self, url='', title=''):
        self.url = url
        self.title = title
        self.replyList = []

    "newply = {'message':message_str, 'meta':dict(), 'member':dict()}"
    def addreply(self,newreply={}):
        if newreply:
            self.replyList.append(newreply)
        else:
            print("bilibili_reply.addreply excepts a reply dict()")
            sys.exit(1)

    def writecsv(self,path,mode="COMPACT"):

        try:
            import csv
        except:
            print('csv module open error')
            sys.exit(1)

        # 文件绝对路径
        print('写入评论信息：')
        path = path + self.title
        f = open(path,'w')
        port_csv = csv.writer(f)

        if mode == "COMPACT":
            port_csv.writerow(['message','rpid','like','uname'])
        else:
            port_csv.writerow(['message'] + list(self.replyList[0]['meta'].keys()) \
                    + list(self.replyList[0]['member']))

            for reply in self.replyList:
                port_csv.writerow([reply['message']] + list(reply['meta'].values()) \
                        + list(reply['member'].values()))

        f.close()
        print('已写入: %s' % path)


def _get_text_via_url(uri):
    try:
        request = requests.get(uri,headers=PROTOCAL.header)
    except requests.exceptions.RequestException as e:
        print(e)

    content = requests.text
    return content


