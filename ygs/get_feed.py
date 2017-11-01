import requests
import threading
import time
import re
import json
from lxml import etree
from bs4 import BeautifulSoup
import traceback
import pymysql
import json
import demjson
import hashlib
import threading
import random

headers = {
'Accept':'application/json, text/javascript, */*; q=0.01',
'Accept-Encoding':'gzip, deflate, br',
'Accept-Language':'zh-CN,zh;q=0.9',
'Connection':'keep-alive',
'Cookie':'_user_identify_=98f16cbc-e3f4-3ced-9a53-485fbcec3e4e; uID=450288; sID=c4008b306cadbf656a185a9dec715d1a; JSESSIONID=aaaBCGvEFFf_S8njIj29v; Hm_lvt_37854ae85b75cf05012d4d71db2a355a=1509418166,1509506676,1509515635; Hm_lpvt_37854ae85b75cf05012d4d71db2a355a=1509515638',
'Host':'www.innotree.cn',
'Referer':'https//www.innotree.cn/inno/database/totalDatabase',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36',
'X-Requested-With':'XMLHttpRequest'
}

seeds_dir = "seeds"

def isexistkey(tjson,tkey):
    if tkey in tjson and tjson[tkey] is not None and tjson[tkey]!="":
        return tjson[tkey]
    else:
        return ""

def get_feed():
    with open('area.json') as f:
        area = f.read().replace("\'", "\"")
        area = json.loads(area)
        print(area)

    with open('round.json') as f:
        round = f.read().replace("\'", "\"")
        round = json.loads(round)
        print(round)

    for a in area:
        for r in round:
            json_file_name = seeds_dir + "/" + str(a['name']) + "_" + str(r['name'])+".txt"
            print(json_file_name)
            url = "https://www.innotree.cn/inno/search/ajax/getCompanySearchResultV2?"
            error_status_cnt = 0
            for st in range(1, 500):
                print(st)
                params = {
                    'areaName': str(a['name']),
                    'rounds': str(r['id']),
                    'st': str(st),
                    'ps': '10',
                    'sEdate': '-1',
                    'sFdate': '1',
                    'sRound': '-1',
                }
                rh = requests.get(url=url, params=params, headers=headers)
                time.sleep(random.random()/50)
                print(rh.status_code)
                if rh.status_code == 200:
                    infos = json.loads(rh.text)
                    print(infos)
                    infos = isexistkey(isexistkey(isexistkey(infos, 'data'), 'company'), 'infos')
                    if 0 != len(infos):
                        error_status_cnt = 0
                    else:
                        error_status_cnt += 1
                    for info in infos:
                        ncid = info['ncid']
                        #print(ncid)
                        with open(json_file_name, "a") as f:
                            f.write(str(ncid) + "\n")
                else:
                    error_status_cnt += 1
                if error_status_cnt >= 10:
                    break

# def test():
#     params = {
#         'areaName':'天津市',
#         'rounds': '1-2',
#         'st': '1',
#         'ps': '10',
#         'sEdate': '-1',
#         'sFdate': '1',
#         'sRound': '-1',
#     }
#     url = "https://www.innotree.cn/inno/search/ajax/getCompanySearchResultV2?"
#     r = requests.get(url, params=params, headers=headers)
#     print(r.headers)
#     print(r.text)

def main():
    get_feed()

if __name__ == '__main__':
    main()