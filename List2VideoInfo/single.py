#!/usr/bin/env python3

#import codecs
import sys, getopt, os
import re
import requests
from bs4 import BeautifulSoup
#import csv


def make_soup(url):

    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
    except:
        print('pyton.requests: %s cannot be opened' % url)
        sys.exit(2)

    # get page title
    vtitle = soup.find('body').find(class_='v-title').string

    # get cid&aid
    idline = soup.find('script',{"type":"text/javascript"},text=re.compile('EmbedPlayer')).text
    cid = re.search('cid=(.*)&aid',idline).group(1)
    aid = re.search('aid=(.*)&pre',idline).group(1)

    # get p-title and cid
    playlist = soup.find(class_='v-plist')
    playlist_videos = playlist.find_all('option')

    # video list count
    count = 0

    if playlist_videos: # check a video list or single video
        print("Video List")
        for _video in playlist_videos:
            ptitle = _video.contents[0][2:]
            link = 'www.bilibili.com' + _video.get('value')
            cid = _video.get('cid')

            outline = '  ' + vtitle + '\n' + ptitle + '\n' + str(aid) + '\n' + str(cid) + '\n' + link
            print(outline)
    else:
        ptitle = vtitle
        cid = 0
        link = url
        print("Single Video")
        outline = '  ' + vtitle + '\n' + ptitle + '\n' + str(aid) + '\n' + str(cid) + '\n' + link
        print(outline)

def main(argv):
    url = str(sys.argv[1])

    make_soup(url)

if __name__ == '__main__':
    main(sys.argv[1:])
