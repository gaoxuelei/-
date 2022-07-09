import time
from selenium import webdriver
import pandas as pd
from bs4 import BeautifulSoup

browser = webdriver.Chrome()
lst = []
url = 'https://weibo.com/login.php'
browser.get(url)
input('登陆后按回车：')
privateCookies = browser.get_cookies()
cookies_dict = {}
for cookie in privateCookies:
    cookies_dict[cookie['name']] = cookie['value']
with open('cookie.txt', 'w', encoding='utf-8') as f:
    f.write(str(cookies_dict))
with open('cookie2.txt', 'w', encoding='utf-8') as f:
    f.write(str(privateCookies))
#browser.close()