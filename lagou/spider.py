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
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'zh-CN,zh;q=0.9',
    'Cache-Control':'max-age=0',
    'Connection':'keep-alive',
    'Host':'www.lagou.com',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36',
    'Cookie':'user_trace_token=20171027164451-89725b01-94a5-4b05-afa8-84258e2cab28; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Fpassport.lagou.com%2Flogin%2Flogin.html%3Fmsg%3Dvalidation%26uStatus%3D2%26clientIp%3D119.139.198.101; LGUID=20171027164452-193535a7-baf3-11e7-962e-5254005c3644; X_HTTP_TOKEN=1bd2f7b5564aa3f79d5e02f5ba573568; JSESSIONID=ABAAABAACBHABBI9AA82E5BA37086560DE936770BBECF1F; ab_test_random_num=0; _putrc=9AADF3D262FFC0CE; login=true; unick=%E6%8B%89%E5%8B%BE%E7%94%A8%E6%88%B73956; hasDeliver=0; _gat=1; LGSID=20171027164452-19353309-baf3-11e7-962e-5254005c3644; LGRID=20171027165100-f516c97b-baf3-11e7-962e-5254005c3644; _ga=GA1.2.693077934.1509093798; _gid=GA1.2.874152868.1509093798; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1509093798; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1509094167'
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
         COLstr=(COLstr+'"%s"'+',')%(key)
         ROWstr=(ROWstr+'"%s"'+',')%(dic[key])
    #cur.execute("INSERT INTO tenantinfo (tenantid,sign) VALUES (\"%s\",0)",(tendant_id))
    COLstr = COLstr.replace("\"","")
    print(COLstr[:-1], ROWstr[:-1])
    #sql = "INSERT INTO %s(%s) VALUES (%s)"%("crawer_company_info_lagou",COLstr[:-1],ROWstr[:-1])"
    try:
        cur.execute("INSERT INTO %s(%s) VALUES (%s)"%("crawer_company_info_co",COLstr[:-1],ROWstr[:-1]))
        cur.connection.commit()
        cur.close()
        conn.close()
    except:
        print(traceback.format_exc())

def generate_id():

    ids = range(100, 30000)
    need_crawl_ids = ids
    return need_crawl_ids

def download_company_notes(id):
    url0 = 'https://www.lagou.com/gongsi/%s.html' % (str(id))
    r0 = requests.get(url0, headers=request_headers)
    return (r0, )

'''
公司名 公司简单描述 公司产品 公司介绍() 公司行业 融资情况 规模 地址 公司标签 面试评价：只爬得分
'''

def crawl(id):
    need = {}
    notes = download_company_notes(id)
    r0 = notes[0]
    print(r0.url)
    tree0 = etree.HTML(r0.content)
    with open("a.html", "wb") as f:
        f.write(etree.tostring(tree0))
    try:
        need['crawler_url'] = r0.url
        need['url_md5'] = hashlib.md5(need['crawler_url'].encode('utf-8')).hexdigest()
        print(need['url_md5'])
        if is_repeat(need['url_md5']):
            return ""
        need['gongsiming'] = tree0.xpath('//div[@class="company_main"]/h1/a')[0].text
        print(need['gongsiming'].strip())
        need['gongsi_jiandan_miaoshu'] = tree0.xpath('/html/body/div[2]/div/div/div[1]/div')[0].text
        print(need['gongsi_jiandan_miaoshu'].strip())
        need['gongsi_jieshao'] = ''.join(tree0.xpath('//span[@class="company_content"]//p/text()')) or \
                                 ''.join(tree0.xpath('//span[@class="company_content"]/text()'))
        print(need['gongsi_jieshao'])

        need['gongsi_dizhi'] = tree0.xpath('//div[contains(@class, "address_container")]//p[contains(@class, "mlist_li_desc")]')[0].text.strip()
        print(need['gongsi_dizhi'])
        need['gongsi_hangye'] = tree0.xpath('//*[@id="basic_container"]/div[2]/ul/li[1]/span')[0].text
        print(need['gongsi_hangye'].strip())
        need['rongzi_qingkuang'] = tree0.xpath('//*[@id="basic_container"]/div[2]/ul/li[2]/span')[0].text
        print(need['rongzi_qingkuang'])
        need['guimo'] = tree0.xpath('//*[@id="basic_container"]/div[2]/ul/li[3]/span')[0].text
        print(need['guimo'])
        need['dizhi'] = tree0.xpath('//*[@id="basic_container"]/div[2]/ul/li[4]/span')[0].text
        print(need['dizhi'])
        gongsi_biaoqian = tree0.xpath('//*[@id="tags_container"]/div[2]/div/ul//li')
        need['gongsi_biaoqian'] = ''
        for bq in gongsi_biaoqian:
            need['gongsi_biaoqian'] += bq.text.strip() + ";"
        print(need['gongsi_biaoqian'])

        zhonghe_pingfen = tree0.xpath('//*[@id="interview_container"]/div[3]/div[1]/div/span[2]')
        zhonghe_pingfen = zhonghe_pingfen[0].text if len(zhonghe_pingfen) else ''
        miaoshu_xiangfu = tree0.xpath('//*[@id="interview_container"]/div[3]/div[1]/ul/li[1]/span[2]')
        miaoshu_xiangfu = miaoshu_xiangfu[0].text if len(miaoshu_xiangfu) else ''
        mianshiguan = tree0.xpath('//*[@id="interview_container"]/div[3]/div[1]/ul/li[2]/span[2]')
        mianshiguan = mianshiguan[0].text if len(mianshiguan) else ''
        gongsi_huanjing = tree0.xpath('//*[@id="interview_container"]/div[3]/div[1]/ul/li[3]/span[2]')
        gongsi_huanjing = gongsi_huanjing[0].text if len(gongsi_huanjing) else ''
        mianshi_pingjia = [zhonghe_pingfen, miaoshu_xiangfu, mianshiguan, gongsi_huanjing]
        need['mianshi_pingjia'] = ''
        for pj in mianshi_pingjia:
            need['mianshi_pingjia'] += pj.strip() + ";"
        print(need['mianshi_pingjia'])
        need['gongsi_chanpin'] = []
    except IndexError:
        print(traceback.format_exc())
        return ""

    try:
        company_products = tree0.xpath('//*[@id="company_products"]/div[2]')[0].xpath('.//div[@class="product_content product_item clearfix"]')
        print(company_products)
        for product in company_products:
            # with open('b.html', 'wb') as f:
            #     f.write(etree.tostring(product))
            chanpin = {}
            chanpin['name'] = product.xpath('.//div[@class="product_url"]/a')[0].text
            chanpin['name'] = str(chanpin['name']).strip()
            print(chanpin['name'])
            putong_gongsi_chanpin_miaoshu = product.xpath('.//div[@class="product_profile"]/p/text()')
            chanpin['miaoshu'] = putong_gongsi_chanpin_miaoshu[0] if putong_gongsi_chanpin_miaoshu else product.xpath('.//div[@class="product_profile"]')[0].text
            chanpin['miaoshu'] = str(chanpin['miaoshu']).strip()
            print(chanpin['miaoshu'])
            #chanpin = json.dumps(chanpin)
            #chanpin = demjson.encode(chanpin)
            need['gongsi_chanpin'].append(chanpin)
        print(need['gongsi_dizhi'])
        print(need['gongsi_chanpin'])
    except IndexError:
        print(traceback.format_exc())
    try:
        write_data_to_mysql(need)
    except Exception as e:
        print(traceback.format_exc())

#公司名 公司简单描述 公司产品 公司介绍() 公司行业 融资情况 规模 地址 公司标签 面试评价：只爬得分
def write_data_to_mysql(dic):
    need = dic
    savemap = {}
    savemap['name'] = need['gongsiming'].strip()
    savemap['company_scale'] = need['guimo'].strip()
    savemap['company_category'] = need['gongsi_hangye'].strip()
    savemap['company_desc'] = need['gongsi_jiandan_miaoshu']
    savemap['company_jieshao'] = need['gongsi_jieshao']
    savemap['company_product'] = demjson.encode(need['gongsi_chanpin'])
    savemap['company_product'] = savemap['company_product'].replace('\"', '\'')
    print(savemap['company_product'], type(savemap['company_product']))
    savemap['company_tags'] = need['gongsi_biaoqian']
    savemap['company_interview_score'] = need['mianshi_pingjia']
    savemap['source'] = 'lagou.com'
    savemap['crawler_url'] = need['crawler_url']
    savemap['dizhi'] = need['gongsi_dizhi']
    savemap['urlMd5'] = need['url_md5']
    for key in savemap.keys():
        savemap[key] = str(savemap[key]).strip()
    store(savemap)

    '''
name	company_nature	
company_scale	company_category	company_desc	dizhi	company_address	company_url	
company_product	company_finance	company_tags	company_interview_score	
company_attention_count	company_depart	company_registrate_time	company_registrate_capital		
company_operate_period	company_operate_range	source		crawler_url urlMd5	addtime
    '''

def main():
    need_crawl_ids = generate_id()
    for id in need_crawl_ids:
        time.sleep(0.2)
        print(id)
        try:
            crawl(id)
        except IndexError as e:
            print(traceback.format_exc())

if __name__ == '__main__':
    main()