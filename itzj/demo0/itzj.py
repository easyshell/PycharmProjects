#-*-coding:utf-8 -*-
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
import config
import demjson
import hashlib

meizhuadao_ids = []

request_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': 'gr_user_id=0c58d572-628f-449f-928b-732828b0afb9; pgv_pvi=1834924032; acw_tc=AQAAACNRFlIhoQEAV8eLd3DDP4Q6T72S; session=01e22a1492ce78da0585e68458e07060d7d245ea; _ga=GA1.2.1506246740.1508830568; _gid=GA1.2.1252954891.1509524390; Hm_lvt_1c587ad486cdb6b962e94fc2002edf89=1508917388,1508922652,1508982946,1509524391; Hm_lpvt_1c587ad486cdb6b962e94fc2002edf89=1509528341; gr_session_id_eee5a46c52000d401f969f4535bdaa78=0e2b7340-6b46-429b-99a3-b195d39810c0',
    'Host': 'www.itjuzi.com',
    'If-Modified-Since': 'Wed, 01 Nov 2017 082130 GMT',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'
}

def is_repeat(url_md5):
    repeatsql = " SELECT urlMd5 from crawer_company_info_co WHERE urlMd5="+ "\"" + (str(url_md5)) + "\""
    print(repeatsql)
    conn = pymysql.connect(config.ip, user=config.user, passwd=config.passwd, port=config.port, db=config.db,
                           charset='utf8')
    cur = conn.cursor()
    cur.execute("set names utf8")
    cur.execute(repeatsql)
    return not(0 == len(cur.fetchall()))

def store(dic):
    conn = pymysql.connect(config.ip,user=config.user,passwd=config.passwd,port=config.port, db=config.db, charset='utf8')
    cur = conn.cursor()
    cur.execute("set names utf8")
    ROWstr=''  #行
    COLstr=''  #列
    for key in dic.keys():
        dic[key] = dic[key].replace("\"", "\'")
        print(key)
        print(dic[key])
        COLstr = COLstr + key + ','
        #COLstr=(COLstr+'"%s"'+',')%(key)
        ROWstr = ROWstr + "\"" + str(dic[key]) + "\"" +  ','
        #ROWstr=(ROWstr+'"%s"'+',')%(dic[key])
    try:
        print(ROWstr[:-1])
        sql  = "INSERT INTO crawer_company_info_itjz (" + COLstr[:-1] + ")" + " VALUES (" + ROWstr[:-1] + ")"
        print(sql)
        cur.execute(sql)
        #cur.execute("INSERT INTO %s(%s) VALUES (%s)"%("crawer_company_info_co",COLstr[:-1],ROWstr[:-1]))
        cur.connection.commit()
        cur.close()
        conn.close()
    except:
        print(traceback.format_exc())

def generate_id():
    ids = range(config.start_id, config.end_id)
    need_crawl_ids = ids
    return need_crawl_ids

def download_company_notes(id):
    url0 = 'https://www.itjuzi.com/investevents/%s' % (str(id))
    r0 = requests.get(url0, headers=request_headers)
    return (r0, )


'''
公司名 公司简单描述 公司产品 公司介绍() 公司行业 融资情况 规模 地址 公司标签 面试评价：只爬得分
'''
need_key = ['crawler_url', 'url_md5', 'gongsiming', 'gongsi_jiandan_miaoshu', 'gongsi_jieshao', 'gongsi_dizhi',\
             'gongsi_hangye', 'rongzi_qingkuang', 'guimo', 'dizhi', 'gongsi_biaoqian', 'mianshi_pingjia', 'gongsi_chanpin']

def crawl(id):
    need = {}
    for key in need_key:
        need[key] = ""
    need['gongsi_chanpin'] = []
    notes = download_company_notes(id)
    r0 = notes[0]
    print(r0.status_code)
    if r0.status_code == 200:
        print(r0.url)
        print(r0.status_code)
    tree0 = etree.HTML(r0.content)
    # with open("a.html", "w") as f:
    #     f.write(etree.tostring(tree0))
    # try:
    #     need['crawler_url'] = r0.url
    #     need['url_md5'] = hashlib.md5(need['crawler_url'].encode('utf-8')).hexdigest()
    #     print(need['url_md5'])
    #     if is_repeat(need['url_md5']):
    #         return ""

    #     gongsiming = tree0.xpath('//div[@class="company_main"]/h1/a')
    #     gongsiming = tree0.xpath('//div[@class="company_word"]')  if not gongsiming else gongsiming
    #     need['gongsiming'] = "" if not gongsiming else gongsiming[0].text
    #     print(need['gongsiming'].strip())
    #     need['gongsi_jiandan_miaoshu'] = tree0.xpath('/html/body/div[2]/div/div/div[1]/div')[0].text
    #     print(need['gongsi_jiandan_miaoshu'].strip())
    #     need['gongsi_jieshao'] = ''.join(tree0.xpath('//span[@class="company_content"]//p/text()')) or \
    #                              ''.join(tree0.xpath('//span[@class="company_content"]/text()'))
    #     print(need['gongsi_jieshao'])
    #     gongsi_dizhi = tree0.xpath('//div[contains(@class, "address_container")]//p[contains(@class, "mlist_li_desc")]')
    #     need['gongsi_dizhi'] = "" if not gongsi_dizhi else gongsi_dizhi[0].text.strip()
    #     print(need['gongsi_dizhi'])
    #     gongsi_hangye = tree0.xpath('//*[@id="basic_container"]/div[2]/ul/li[1]/span')
    #     need['gongsi_hangye'] = "" if not gongsi_hangye else gongsi_hangye[0].text.strip()
    #     print(need['gongsi_hangye'].strip())
    #     rongzi_qingkuang = tree0.xpath('//*[@id="basic_container"]/div[2]/ul/li[2]/span')
    #     need['rongzi_qingkuang'] = "" if not rongzi_qingkuang else rongzi_qingkuang[0].text.strip()
    #     print(need['rongzi_qingkuang'])
    #     guimo = tree0.xpath('//*[@id="basic_container"]/div[2]/ul/li[3]/span')
    #     need['guimo'] = "" if not guimo else guimo[0].text.strip()
    #     print(need['guimo'])
    #     dizhi = tree0.xpath('//*[@id="basic_container"]/div[2]/ul/li[4]/span')
    #     need['dizhi'] = "" if not dizhi else dizhi[0].text.strip()
    #     print(need['dizhi'])
    #     gongsi_biaoqian = tree0.xpath('//*[@id="tags_container"]/div[2]/div/ul//li')
    #     need['gongsi_biaoqian'] = ''
    #     for bq in gongsi_biaoqian:
    #         need['gongsi_biaoqian'] += bq.text.strip() + ";"
    #     print(need['gongsi_biaoqian'])
    #     zhonghe_pingfen = tree0.xpath('//*[@id="interview_container"]/div[3]/div[1]/div/span[2]')
    #     zhonghe_pingfen = zhonghe_pingfen[0].text if len(zhonghe_pingfen) else ''
    #     miaoshu_xiangfu = tree0.xpath('//*[@id="interview_container"]/div[3]/div[1]/ul/li[1]/span[2]')
    #     miaoshu_xiangfu = miaoshu_xiangfu[0].text if len(miaoshu_xiangfu) else ''
    #     mianshiguan = tree0.xpath('//*[@id="interview_container"]/div[3]/div[1]/ul/li[2]/span[2]')
    #     mianshiguan = mianshiguan[0].text if len(mianshiguan) else ''
    #     gongsi_huanjing = tree0.xpath('//*[@id="interview_container"]/div[3]/div[1]/ul/li[3]/span[2]')
    #     gongsi_huanjing = gongsi_huanjing[0].text if len(gongsi_huanjing) else ''
    #     mianshi_pingjia = [zhonghe_pingfen, miaoshu_xiangfu, mianshiguan, gongsi_huanjing]
    #     need['mianshi_pingjia'] = ''
    #     for pj in mianshi_pingjia:
    #         need['mianshi_pingjia'] += pj.strip() + ";"
    #     print(need['mianshi_pingjia'])
    #     company_products = tree0.xpath('//*[@id="company_products"]/div[2]')
    #     company_products = [] if not company_products else company_products[0]
    #     company_products = [] if not company_products else company_products.xpath('.//div[@class="product_content product_item clearfix"]')
    #
    #     print(company_products)
    #     for product in company_products:
    #         # with open('b.html', 'wb') as f:
    #         #     f.write(etree.tostring(product))
    #         chanpin = {}
    #         chanpin['name'] = product.xpath('.//div[@class="product_url"]/a')[0].text
    #         chanpin['name'] = str(chanpin['name']).strip()
    #         print(chanpin['name'])
    #         putong_gongsi_chanpin_miaoshu = product.xpath('.//div[@class="product_profile"]/p/text()')
    #         chanpin['miaoshu'] = putong_gongsi_chanpin_miaoshu[0] if putong_gongsi_chanpin_miaoshu else product.xpath('.//div[@class="product_profile"]')[0].text
    #         chanpin['miaoshu'] = str(chanpin['miaoshu']).strip()
    #         print(chanpin['miaoshu'])
    #         need['gongsi_chanpin'].append(chanpin)
    #
    #     need['gongsi_chanpin'] = json.dumps(need['gongsi_chanpin'], ensure_ascii=False)
    #     print(need['gongsi_dizhi'])
    #     print(need['gongsi_chanpin'])
    #     lagou_renzheng_zhuangtai = tree0.xpath('//a[contains(@class, "identification")]/span')[0].text
    #     need['lagou_renzheng_zhuangtai'] = '' if not lagou_renzheng_zhuangtai else lagou_renzheng_zhuangtai
    #     print(need['lagou_renzheng_zhuangtai'])
    #
    #     jianli_chuli = tree0.xpath('//div[contains(@class, "company_data")]//strong')
    #     print(jianli_chuli)
    #     jianli_chuli = [e.text.strip() for e in jianli_chuli]
    #     print(jianli_chuli)
    #     zhaopin_data = {}
    #     zhaopin_data['zhaopin_zhiwei_shu'] = '' if not jianli_chuli[0] else jianli_chuli[0]
    #     zhaopin_data['jianli_jishi_chulilv'] = '' if not jianli_chuli[1] else jianli_chuli[1]
    #     zhaopin_data['jianli_chuli_yongshi'] = '' if not jianli_chuli[2] else jianli_chuli[2]
    #     zhaopin_data['mianshi_pingjia_geshu'] = '' if not jianli_chuli[3] else jianli_chuli[3]
    #     zhaopin_data['qiye_zuijin_denglu'] = '' if not jianli_chuli[4] else jianli_chuli[4]
    #     need['zhaopin_data'] = []
    #     need['zhaopin_data'] = json.dumps(zhaopin_data, ensure_ascii=False)
    #
    #     try:
    #         write_data_to_mysql(need)
    #     except Exception as e:
    #         print(traceback.format_exc())
    #         return 0
    # except IndexError:
    #     if need['gongsiming'] and not is_repeat(need['url_md5']):
    #         write_data_to_mysql(need)
    #     print(traceback.format_exc())

#公司名 公司简单描述 公司产品 公司介绍() 公司行业 融资情况 规模 地址 公司标签 面试评价：只爬得分
def write_data_to_mysql(dic):
    need = dic
    print(need.keys())
    savemap = {}
    savemap['name'] = need['gongsiming'].strip()
    savemap['company_scale'] = need['guimo'].strip()
    savemap['company_category'] = need['gongsi_hangye'].strip()
    savemap['company_desc'] = need['gongsi_jiandan_miaoshu']
    savemap['company_jieshao'] = need['gongsi_jieshao']
    savemap['company_product'] = need['gongsi_chanpin']
    savemap['company_product'] = savemap['company_product']
    print(savemap['company_product'], type(savemap['company_product']))
    savemap['company_tags'] = need['gongsi_biaoqian']
    savemap['company_interview_score'] = need['mianshi_pingjia']
    savemap['source'] = 'lagou.com'
    savemap['crawler_url'] = need['crawler_url']
    savemap['urlMd5'] = need['url_md5']
    savemap['dizhi'] = need['dizhi']
    savemap['company_finance'] = need['rongzi_qingkuang']
    savemap['renzheng_zhuangtai'] = need['lagou_renzheng_zhuangtai']
    savemap['zhaopin_shuju'] = need['zhaopin_data']

    for key in savemap.keys():
        savemap[key] = str(savemap[key]).strip()
    store(savemap)

def main():
    need_crawl_ids = generate_id()
    for id in need_crawl_ids:
        time.sleep(0.02)
        print(id)
        try:
            crawl(id)
        except IndexError as e:
            print(traceback.format_exc())

if __name__ == '__main__':
    main()