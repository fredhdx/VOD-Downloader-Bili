#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

class bilibili_video:
    "store bilibili video info (single)"
    "信息分别储存于: meta和play两个字典里"
    "methods: update(ditionary), write(list of key values)"

    def __init__(self, args={}):
        self.meta = {'title':'', 'aid':'', 'cid':'', 'pubdate':0, 'senddate':0, 'uploadtime':'',
                     'duration':'', 'category':'', 'tag':'', 'description':''}
        self.play = {'view':0, 'favorite':0, 'coin':0, 'danmaku':0, 'reply':0, 'share':0}
        self.up = {'author':'', 'mid':'', 'upspace':''}
        self.urls = {'vurl':'', 'picurl':''}

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
                    self.play[k_args] = args[k_args]
                elif k_args in self.urls:
                    self.urls[k_args] = args[k_args]
                else:
                    print("Warning: key %s not found in bilibili_video" % k_args)

    # kargs should be list of keys
    def write(self,kargs=[]):
        if not kargs:
            outline = list(self.meta.items()) + list(self.play.items()) + list(self.up.items()) + list(self.urls.items())
        else:
            outline = []
            for key in kargs:
                if key in self.meta:
                    outline.append('(' + key + ',' + str(self.meta[key]) + ')')
                elif key in self.play:
                    outline.append('(' + key + ',' + str(self.play[key]) + ')')
                elif key in self.up:
                    outline.append('(' + key + ',' + str(self.up[key]) + ')')
                elif key in self.urls:
                    outline.append('(' + key + ',' + str(self.urls[key]) + ')')
                else:
                    print("Warning: key %s not found in bilibili_video" % key)

        print(outline)

    def writevalue(self):
        row = list(self.meta.values()) + list(self.play.values()) + list(self.up.values()) + list(self.urls.values())
        return row

    def writekey(self):
        row = list(self.meta.keys()) + list(self.play.keys()) + list(self.up.keys()) + list(self.urls.keys())
        return row

    def writestatkey(self):
        row = ['标题', 'aid', 'pubdate', '时长', '播放数', '分享', '收藏', '硬币', '弹幕', '评论', '作者', '简介', '分类', '标签', '链接']
        return row

    def writestat(self):
        row = [ self.meta['title'], self.meta['aid'], self.meta['pubdate'], self.meta['duration'],
                self.play['view'], self.play['share'], self.play['favorite'], self.play['coin'], self.play['danmaku'], self.play['reply'],
                self.up['author'],
                self.meta['description'],
                self.meta['category'], self.meta['tag'],
                self.urls['vurl']
                ]
        return row