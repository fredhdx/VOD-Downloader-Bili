#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys, getopt, os
import requests
from bs4 import BeautifulSoup
import csv
import shutil
import traceback

# prepare save DIRECTORY
DIRECTORY = os.getcwd()
# DIRECTORY = os.path.dirname(os.path.abspath(__file__))
SAVE_DIRECTORY = DIRECTORY + '/result'


class Vpiece:
    _vtitle = "n/a"
    _ptitle = "n/a"
    _aid = 0
    _cid = 0
    _link = ""
    _id = 0

    def __init__(self,vtitle,ptitle,aid,cid,link, iid):
        self._vtitle = vtitle
        self._ptitle = ptitle
        self._aid = aid
        self._cid = cid
        self._link = link
        self._iid = iid

    def getvtitle(self):
        return self._vtitle
    def getptitle(self):
        return self._ptitle
    def getaid(self):
        return self._aid
    def getcid(self):
        return self._cid
    def getlink(self):
        return self._link
    def getid(self):
        return self._iid

    def info(self):
        print("Video title: %s" % self._vtitle)
        print("    p title: %s" % self._ptitle)
        print("        aid: %d" % self._aid)
        print("        cid: %d" % self._cid)
        print("       link: %d" % self._link)
        print("         id: %d" % self._id)

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

    lsp_pattern = re.compile(r'[\x80-\xFF]')
    text = lsp_pattern.sub('', text)

    return text

def make_soup(url,port_csv, vlist):
    # make soup
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
    except:
        print('pyton.requests: %s cannot be opened' % url)
        sys.exit(2)

    # get page title
    vtitle = soup.find('body').find(class_='v-title').string
    vtitle = remove_nbws(vtitle)

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
        for _video in playlist_videos:
            ptitle = _video.contents[0][2:]
            ptitle = remove_nbws(ptitle)
            link = 'https://www.bilibili.com' + _video.get('value')
            cid = _video.get('cid')
            item = Vpiece(vtitle, ptitle, aid, cid, link, count)

            if count == 0:
                port_csv.writerow([vtitle,ptitle,link,aid,cid])
            else:
                port_csv.writerow(['',ptitle,link,aid,cid])

            vlist.append(item)
            count = count + 1
    else:
        ptitle = vtitle
        link = url
        cid = 0
        item = Vpiece(vtitle, ptitle, aid, cid, link, count)

        port_csv.writerow([vtitle,ptitle,link,aid,cid])
        vlist.append(item)

def write_vlist_csv(fn,vlist):

    # open output csv file
    fo = open(fn + '2.csv','w')
    port_csv = csv.writer(fo)
    port_csv.writerow(['title','p-title','link','aid','cid'])

    if not vlist:
        print("write_vlist_csv: error: vlist empty")
    else:
        for v in vlist:
            if v.getid() == 0:
                port_csv.writerow([v.getvtitle(),v.getptitle(),v.getlink(),v.getaid(),v.getcid()])
            else:
                port_csv.writerow(['',v.getptitle(),v.getlink(),v.getaid(),v.getcid()])

    # move output file to save location
    fo.close()
    shutil.move(DIRECTORY + '/' + fn + '2.csv', SAVE_DIRECTORY + '/' + fn + '2.csv')


# write to csv with keyword: exclude mode available
def write_vlist_csv_key(fn,vlist,key, exclude=0):

    # open output csv file
    if exclude == 0:
        outname = fn + "_" + key + ".csv"
    elif exclude == 1:
        outname = fn + "_ex" + key + ".csv"
    fo = open(outname, 'w')

    port_csv = csv.writer(fo)
    port_csv.writerow(['title','p-title','link','aid','cid'])

    if not vlist:
        print("write_vlist_csv: error: vlist empty")
    else:
        extitle = ''
        for v in vlist:
            if (exclude == 1) != (key in v.getptitle()):
                vtitle = v.getvtitle()
                if vtitle != extitle:
                    port_csv.writerow([vtitle,v.getptitle(),v.getlink(),v.getaid(),v.getcid()])
                else:
                    port_csv.writerow(['',v.getptitle(),v.getlink(),v.getaid(),v.getcid()])

                extitle = vtitle

    # move output file to save location
    fo.close()
    shutil.move(DIRECTORY + '/' + outname, SAVE_DIRECTORY + '/' + outname)



def write_md(fn,vlist):
    fo = open(fn,'w')
    if not vlist:
        print("write_md: error: vlist empty")
    else:
        title = ""
        for v in vlist:
            if v.getid() == 0:
                title = v.getvtitle()
                fo.write('\n[' + title + ' ' + v.getptitle() + ']' + '(' + v.getlink() + ')\n')
            else:
                fo.write('[' + title + ' ' + v.getptitle() + ']' + '(' + v.getlink() + ')\n')

    # move output file to save location
    fo.close()
    shutil.move(DIRECTORY + '/' + fn, SAVE_DIRECTORY + '/' + fn)


def main(argv):
    try:
       opts, args = getopt.getopt(argv,"hi:",["ifile="])
    except getopt.GetoptError:
       print('-i <inputfile>')
       sys.exit(2)

    for opt, arg in opts:
       if opt == '-h':
          print('-i <inputfile>')
          sys.exit()
       elif opt in ("-i", "--ifile"):
          inputfile = arg

    # extract output file name from input
    outputfile = os.path.splitext(inputfile)[0]

    # default csv writer
    fo = open(outputfile + ".csv",'w')
    port_csv = csv.writer(fo)
    port_csv.writerow(['title','p-title','link','aid', 'cid'])

    global SAVE_DIRECTORY
    try:
        os.stat(SAVE_DIRECTORY)
    except:
        os.mkdir(SAVE_DIRECTORY)

    # make soup
    vlist = []
    count = 1
    with open(inputfile,'r') as f:
        for line in f:
            if 'bilibili' in line:
                print('%d. Processing link: %s ' % (count, line.strip()))
                try:
                    make_soup(line.strip(),port_csv,vlist)
                except Exception as e:
                    print(e)
                    traceback.print_exc()
                count += 1
    print(DIRECTORY)

    if vlist:
       write_vlist_csv(outputfile,vlist)
       write_vlist_csv_key(outputfile,vlist,"MC",exclude=0)
       write_vlist_csv_key(outputfile,vlist,"MC",exclude=1)
       write_md("md_list.md",vlist)
    fo.close()

    shutil.move(DIRECTORY + '/' + outputfile + '.csv', SAVE_DIRECTORY + '/' + outputfile + '.csv')

    print("Finished. If you are using Windows + Excel, please set Options->Language->Chinese as default.")
    print("转码完毕。如果您使用Windows系统并用Excel打开csv, 请更改选项->语言->中文为默认语言。")

if __name__ == '__main__':
    main(sys.argv[1:])
