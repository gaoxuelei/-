import time
import datetime
from selenium import webdriver
import pandas as pd
from bs4 import BeautifulSoup

# 微博时间转换
def zhuan_dd(dd):
    GMT_FORMAT = '%a %b %d %H:%M:%S +0800 %Y'
    timeArray = datetime.datetime.strptime(dd, GMT_FORMAT)
    aa = timeArray.strftime("%Y-%m-%d %H:%M:%S")
    return aa


browser = webdriver.Chrome()
# 防检测
browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
  "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    })
  """
})
lst = []

url = 'https://d.weibo.com/102803_ctg1_4188_-_ctg1_4188?from=faxian_hot&mod=fenlei#'

browser.get(url)
time.sleep(10)

with open('cookie2.txt', 'r') as f:
    s = f.read()

cookies = eval(s)

for cookie in cookies:
    browser.add_cookie(
        {
            'domain': cookie['domain'],
            'name': cookie['name'],
            'value': cookie['value'],
            'path': cookie['path']
        }
    )
# # 刷新页面
browser.refresh()
time.sleep(5)
browser.get(url)
# 下拉
js = "var q=document.documentElement.scrollTop=100000"
browser.execute_script(js)
time.sleep(3)
js = "var q=document.documentElement.scrollTop=100000"
browser.execute_script(js)
time.sleep(3)

js = "var q=document.documentElement.scrollTop=0"
browser.execute_script(js)
time.sleep(3)

soup = BeautifulSoup(browser.page_source, 'lxml') # 使用BeautifulSoup库解析网址
sj_lst = soup.select('.WB_from.S_txt2')

for i in sj_lst:
    lst.append(i.select('a')[0]['href']) # a标签里的内容

with open('1.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lst[0:10]))

# browser.quit()


import requests
import urllib
from bs4 import BeautifulSoup

import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['微博']
datatabel = db['博文1']
datatabel2 = db['博文2']

datatabel.drop()

datatabel2.drop()

tag_lst = []
lst1 = []
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
with open('cookie.txt', 'r') as f:
    s = f.read()
cookies = eval(s)
with open('1.txt', 'r') as f:
    s2 = f.read()
weibo_lst = s2.split('\n')
weibo_lst2 = []
for url in weibo_lst:
    sid = url.split('/')[-1].split('?')[0]
    url2 = 'https://weibo.com/ajax/statuses/show?id={}'.format(sid)
    html = requests.get(url=url2, headers=headers, cookies=cookies)
    sj_lst = html.json()
    data = {}
    data['博文链接'] = url
    data['发表人'] = sj_lst['user']['screen_name']
    data['发表时间'] = zhuan_dd(sj_lst['created_at'])
    data['发表人ID'] = sj_lst['user']['idstr']

    try:
        url_long = 'https://weibo.com/ajax/statuses/longtext?id={}'.format(sid)
        html = requests.get(url=url_long, headers=headers, timeout=5, cookies=cookies)
        data['博文内容'] = html.json()['data']['longTextContent']
    except:
        data['博文内容'] = sj_lst['text_raw'].strip()
    data['转发数'] = sj_lst['reposts_count']
    data['评论数'] = sj_lst['comments_count']
    data['点赞数'] = sj_lst['attitudes_count']
    try:
        ls = []
        tag = sj_lst['topic_struct']
        for k in tag:
            tag_lst.append(k['topic_title'])
            ls.append(k['topic_title'])
        data['标签'] = '&'.join(ls)
    except:
        pass
    print(data)
    lst1.append(data)
    datatabel.insert_one(data)

result = pd.DataFrame(lst1)
result.drop_duplicates(subset=['博文链接'], keep='first', inplace=True)
result.to_excel('博文1.xlsx', index=None)

lst1 = []
try:
    tag_lst2 = list(set(tag_lst))
    for keywords in tag_lst2:
        url = 'https://s.weibo.com/weibo?q={}'.format(urllib.parse.quote('#' + keywords + '#'))
        html = requests.get(url=url, headers=headers, cookies=cookies)
        soup = BeautifulSoup(html.text, 'lxml')
        sj_lst = soup.select('.card-feed')
        for i in sj_lst[0:10]:
            ls = i.select('.from a')[0]['href']
            ls2 = 'https:' + ls.replace('?refer_flag=1001030103_', '')
            weibo_lst2.append(ls2)

    for url in weibo_lst2:
        sid = url.split('/')[-1]
        url2 = 'https://weibo.com/ajax/statuses/show?id={}'.format(sid)
        try:
            html = requests.get(url=url2, headers=headers, cookies=cookies)
            sj_lst = html.json()
            data = {}
            data['博文链接'] = url
            data['发表人'] = sj_lst['user']['screen_name']
            data['发表时间'] = zhuan_dd(sj_lst['created_at'])
            data['发表人ID'] = sj_lst['user']['idstr']
            try:
                url_long = 'https://weibo.com/ajax/statuses/longtext?id={}'.format(sid)
                html = requests.get(url=url_long, headers=headers, timeout=5, cookies=cookies)
                data['博文内容'] = html.json()['data']['longTextContent']
            except:
                data['博文内容'] = sj_lst['text_raw'].strip()
            data['转发数'] = sj_lst['reposts_count']
            data['评论数'] = sj_lst['comments_count']
            data['点赞数'] = sj_lst['attitudes_count']
            try:
                ls = []
                tag = sj_lst['topic_struct']
                for k in tag:
                    tag_lst.append(k['topic_title'])
                    ls.append(k['topic_title'])
                data['标签'] = '&'.join(ls)
            except:
                pass
            print(data)
            lst1.append(data)
            datatabel2.insert_one(data)
        except:
            pass

    result = pd.DataFrame(lst1)
    result.drop_duplicates(subset=['博文链接'], keep='first', inplace=True)
    result.to_excel('博文2.xlsx', index=None)

except:
    pass

import requests
import pandas as pd
import time
import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['微博']
datatabel = db['评论1']
datatabel.drop()
import datetime


def zhuan_dd(dd):
    GMT_FORMAT = '%a %b %d %H:%M:%S +0800 %Y'
    timeArray = datetime.datetime.strptime(dd, GMT_FORMAT)
    aa = timeArray.strftime("%Y-%m-%d %H:%M:%S")
    return aa


lst = []
lst2 = []
error = []
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
lst = pd.read_excel('博文1.xlsx')['博文链接']
for url1 in lst:
    url2 = 'https://weibo.com/ajax/statuses/show?id={}'.format(url1.split('/')[4].split('?')[0])
    try:
        html = requests.get(url=url2, headers=headers, timeout=5)
        mid = html.json()['mid']
        total_number = html.json()['comments_count']
        url = 'https://weibo.com/ajax/statuses/buildComments?is_reload=1&id={}&is_show_bulletin=2&is_mix=0&count=20'.format(
            mid)
        html = requests.get(url=url, headers=headers, timeout=5)
        next_sid = html.json()['max_id'] #下一条mid可以从当前max_id获取
        sj_lst = html.json()['data']
        for i in sj_lst[0:10]:
            data = {}
            data['博文id'] = str(mid)
            data['博文链接'] = url1
            data['创建时间'] = zhuan_dd(i['created_at'])
            data['点赞数'] = i['like_counts']
            data['回复数'] = i['total_number']
            data['评论内容'] = i['text_raw']
            data['评论id'] = str(i['id'])
            data['评论人昵称'] = i['user'].get('name')
            data['评论人id'] = str(i['user'].get('idstr'))
            lst2.append(data)
            datatabel.insert_one(data)
        print('ok')
    except:
        pass
result = pd.DataFrame(lst2)
result.to_excel('评论1.xlsx', index=None)

try:
    import requests
    import pandas as pd
    import time
    import pymongo

    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client['微博']
    datatabel = db['评论2']
    datatabel.drop()
    import datetime


    def zhuan_dd(dd):
        GMT_FORMAT = '%a %b %d %H:%M:%S +0800 %Y'
        timeArray = datetime.datetime.strptime(dd, GMT_FORMAT)
        aa = timeArray.strftime("%Y-%m-%d %H:%M:%S")
        return aa


    lst = []
    lst2 = []
    error = []
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
    lst = pd.read_excel('博文2.xlsx')['博文链接']
    for url1 in lst:
        url2 = 'https://weibo.com/ajax/statuses/show?id={}'.format(url1.split('/')[4].split('?')[0])
        try:
            html = requests.get(url=url2, headers=headers, timeout=5)
            mid = html.json()['mid']
            total_number = html.json()['comments_count']
            url = 'https://weibo.com/ajax/statuses/buildComments?is_reload=1&id={}&is_show_bulletin=2&is_mix=0&count=20'.format(
                mid)
            html = requests.get(url=url, headers=headers, timeout=5)
            next_sid = html.json()['max_id']
            sj_lst = html.json()['data']
            for i in sj_lst[0:10]:
                data = {}
                data['博文id'] = str(mid)
                data['博文链接'] = url1
                data['创建时间'] = zhuan_dd(i['created_at'])
                data['点赞数'] = i['like_counts']
                data['回复数'] = i['total_number']
                data['评论内容'] = i['text_raw']
                data['评论id'] = str(i['id'])
                data['评论人昵称'] = i['user'].get('name')
                data['评论人id'] = str(i['user'].get('idstr'))
                lst2.append(data)
                datatabel.insert_one(data)
            print('ok')
        except:
            pass
    result = pd.DataFrame(lst2)
    result.to_excel('评论2.xlsx', index=None)
except:
    pass
