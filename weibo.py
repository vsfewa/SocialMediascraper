import time
from selenium.common.exceptions import NoSuchElementException
import requests
from lxml import html
from selenium import webdriver
import json
import pandas as pd


def is_number(uchar):
    if u'\u0030' <= uchar <= u'\u0039':
        return True
    else:
        return False


def format_str(content):
    content_str = ''
    num = 0
    if content.find(u"万") != -1:
        num = num + 4
    if content.find(u"亿") != -1:
        num = num + 8
    for i in content:
        if is_number(i):
            content_str = content_str + i
        elif i == '.':
            num = num - 1
    for i in range(0, num):
        content_str = content_str + '0'
    return content_str


def convert_list(str):
    return str.replace('[', '').replace(']', '').replace('\'', '').replace(':', '')


new_info = {'标题': [], '热度': [], '转发数': [], '评论数': []}
temp = {'标题': []}

headers = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.114 Safari/537.36',
    'Cookie': 'SINAGLOBAL=1318380576986.9216.1618412840342; '
              'SUB=_2A25Nc3UWDeRhGeBH6VYR9i7FyD2IHXVunBterDV8PUJbkNANLUWskW1NQdlDclhI81Tr5-7iH9FcYJ8jQ0Wx-pBf; '
              'SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWvpzxnLSZU7CSUWsxJN8O65NHD95Qc1KzXehq71KepWs4DqcjlKgvE9gvV9'
              '-Ufd0zc1K-R; _s_tentry=-; Apache=2855260797579.704.1618484155267; '
              'ULV=1618484155274:3:3:3:2855260797579.704.1618484155267:1618473867936; '
              'WBStorage=8daec78e6a891122|undefined'
}
url = 'https://s.weibo.com/top/summary'  # 需要爬数据的网址
page = requests.Session().get(url, headers=headers)
page.encoding = 'utf-8'
tree = html.fromstring(page.text)
index_list2 = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
cookie_path = 'D:\\cookies\\cookies.txt'
topic_list = tree.xpath('//td[@class="td-02"]//a/text()')
hot_num = tree.xpath('//td[@class="td-02"]//span/text()')
del topic_list[0]
url_list = tree.xpath('//td[@class="td-02"]//a/@href')  # 获取需要的数据
del url_list[0]


def parse_news():
    for i in range(0, 10):
        new_info['标题'].append(topic_list[i])
        new_info['热度'].append(hot_num[i])
        temp['标题'].append(topic_list[i])


parse_news()


# cookie_path = 'E:\cookies\cookies.txt'
# with open(cookie_path, 'r', encoding='ANSI') as f:
#     cookies_str = f.read()
# cookies_list = json.loads(cookies_str)
# browser = webdriver.Chrome(executable_path='E:\pyjj\chromedriver.exe')
# browser.get(url)
# browser.delete_all_cookies()
# for jsonObj in cookies_list:
#     browser.add_cookie({
#         'domain': jsonObj["domain"],
#         'name': jsonObj['name'],
#         'value': jsonObj['value'],
#         'path': jsonObj["path"],
#         'expires': None
#     })
# browser.get(url)
# comment_button = browser.find_element_by_xpath('//*[@id="pl_feedlist_index"]/div[1]/div[1]/div[2]/div[2]/ul/li[3]/a')
# comment_button.click()
# time.sleep(5)
# comment_list = browser.find_element_by_xpath('//*[@id="pl_feedlist_index"]/div[1]/div[1]/div[2]/div['
#                                              '3]/div/div[2]/div[2]/div[1]').get_attribute('comment_id')
# print(comment_list)


def parse_review():
    for i in range(0, 10):
        new_url = 'https://s.weibo.com/' + url_list[i]
        with open(cookie_path, 'r', encoding='ANSI') as f:
            cookies_str = f.read()
        cookies_list = json.loads(cookies_str)
        browser = webdriver.Chrome(executable_path='D:\pyjj\chromedriver.exe')
        browser.get(new_url)
        for jsonObj in cookies_list:
            browser.add_cookie({
                'domain': jsonObj["domain"],
                'name': jsonObj['name'],
                'value': jsonObj['value'],
                'path': jsonObj["path"],
                'expires': None
            })
        browser.get(new_url)
        time.sleep(1)
        try:
            forward = format_str(
            browser.find_element_by_xpath('//*[@id="pl_feedlist_index"]/div[1]/div[2]/div[2]/div[2]/ul/li[2]/a').text)
            discuss = format_str(
            browser.find_element_by_xpath('//*[@id="pl_feedlist_index"]/div[1]/div[2]/div[2]/div[2]/ul/li[3]/a').text)
            new_info['转发数'].append(forward)
            new_info['评论数'].append(discuss)
        except NoSuchElementException:
            del(new_info['标题'][i])
            del(new_info['热度'][i])
            continue
        else:
            try:
                comment_button = browser.find_element_by_xpath(
                '//*[@id="pl_feedlist_index"]/div[1]/div[1]/div[2]/div[2]/ul/li[3]/a')
            except NoSuchElementException:
                comment_button = browser.find_element_by_xpath(
                '//*[@id="pl_feedlist_index"]/div[1]/div[2]/div[2]/div[2]/ul/li[3]/a')
            finally:
                comment_button.click()
                time.sleep(3)
                review_info = {'用户名': [], '内容': [], '点赞数': []}
                for j in index_list2:
                    try:
                        user = browser.find_element_by_xpath(
                        '//*[@id="pl_feedlist_index"]/div[1]/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[' + j + ']/div[2]/div[1]/a').text
                        review_info['用户名'].append(user)
                    except NoSuchElementException:
                        break
                    else:
                        content = browser.find_element_by_xpath(
                        '//*[@id="pl_feedlist_index"]/div[1]/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[' + j + ']/div[2]/div[1]').text.replace(
                        user, '').replace('\n', '').replace('\r', '').replace(' ', '').replace('：', '')
                        like = browser.find_element_by_xpath(
                        '//*[@id="pl_feedlist_index"]/div[1]/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[' + j + ']/div[2]/div[2]/ul/li[3]/a/span').text
                        rtime = browser.find_element_by_xpath(
                        '//*[@id="pl_feedlist_index"]/div[1]/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[' + j + ']/div[2]/div[2]/p').text
                        review_info['内容'].append(content)
                        review_info['点赞数'].append(like)
                print(review_info)
                reviews_info = pd.DataFrame(review_info)
                reviews_info.to_csv('' + convert_list(str(temp['标题'][i])) + '热评.txt', encoding='utf_8_sig', index=False)
        browser.close()
    browser.quit()



parse_review()
news_info = pd.DataFrame(new_info)
news_info.to_csv('5.19微博热搜信息.txt', encoding='utf_8_sig', index=False)
