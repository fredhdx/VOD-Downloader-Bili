header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
    AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/35.0.1916.114 Safari/537.36',
    'Cookie': 'AspxAutoDetectCookieSupport=1'
}

timeout=None

scheme = "http://"
CHARSET = "utf-8"

web = {'Bilibili':'www.bilibili.com'}

Bilibili_API = {'search':'https://search.bilibili.com/all?keyword=%(_keyword)s&page=', \
        'info':'interface.bilibili.com/player?id=cid:%(_cid)s&aid=%(_aid)s', \
        'archive':'api.bilibili.com/archive_stat/stat?aid=%(_aid)s', \
        'replyList':'http://api.bilibili.cn/feedback?aid=%(_aid)s',\
        'reply':'api.bilibili.com/x/reply?jsonp=jsonp&type=1&sort=0&pn=%(_pn)s&nohot=%(_nohot)s&oid=%(_aid)s', \
        'tag': 'https://api.bilibili.com/x/tag/archive/tags?&aid=%(_aid)s'}

SNH_API = {'live':'http://live.snh48.com'}
