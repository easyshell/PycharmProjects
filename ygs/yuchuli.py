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

headers = {
    'Accept':'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'zh-CN,zh;q=0.9',
    'Connection':'keep-alive',
    'Cookie':'_user_identify_=98f16cbc-e3f4-3ced-9a53-485fbcec3e4e; uID=450288; sID=c4008b306cadbf656a185a9dec715d1a; JSESSIONID=aaadSkmIwytWI4tRwN19v; Hm_lvt_37854ae85b75cf05012d4d71db2a355a=1509418166,1509506676; Hm_lpvt_37854ae85b75cf05012d4d71db2a355a=1509506679',
    'Host':'www.innotree.cn',
    'Referer':'https://www.innotree.cn/inno/database/totalDatabase',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36',
    'X-Requested-With':'XMLHttpRequest'
}


def get_area_round():
    url = "https://www.innotree.cn/inno/screening/ajax/getAllScreeningsForInvestDB"
    r = requests.get(url, headers=headers)
    js = json.loads(r.text)
    area_list = js['data']['areaList']
    round_list = js['data']['roundList']
    print(area_list)
    print(round_list)
    with open('area.json', 'w') as f:
        f.write(json.dumps(area_list, ensure_ascii=False))
    with open('round.json', 'w') as f:
        f.write(json.dumps(round_list, ensure_ascii=False))

def main():
    get_area_round()



if __name__ == '__main__':
    main()