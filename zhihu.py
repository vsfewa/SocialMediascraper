import time
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
import json
import pandas as pd
import re


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
    return str.replace('[', '').replace(']', '').replace('\'', '').replace('?', '')


new_info = {'标题': [], '回答': [], '评论': [], '浏览量': []}

url = 'https://www.zhihu.com/hot'  # 需要爬数据的网址
cookie_path = 'D:\\cookies\\zhihu.txt'
url_list = []
index_list1 = ['1', '2', '3', '4', '5', '6', '7']
index_list2 = ['1', '2', '3', '4', '5', '6', '7', '8','9','10']
with open(cookie_path, 'r', encoding='ANSI') as f:
    cookies_str = f.read()
cookies_list = json.loads(cookies_str)
browser = webdriver.Chrome(executable_path='D:\pyjj\chromedriver.exe')
browser.get(url)
for jsonObj in cookies_list:
    browser.add_cookie({
        'domain': jsonObj["domain"],
        'name': jsonObj['name'],
        'value': jsonObj['value'],
        'path': jsonObj["path"],
        'expires': None
    })
browser.get(url)
for i in index_list2:
    title = browser.find_element_by_xpath('//*[@id="TopstoryContent"]/div/div/div[2]/section['+i+']/div[2]/a/h2').text
    new_info['标题'].append(title)
    url = browser.find_element_by_xpath('//*[@id="TopstoryContent"]/div/div/div[2]/section['+i+']/div[2]/a').get_attribute('href')
    url_list.append(url)

# 动态加载网页使用selenium
def parse_review():
    for i in range(0, 10):
        new_url = convert_list(str(url_list[i]))
        browser.get(new_url)
        time.sleep(1)
        try:
            read = format_str(browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div[1]/div[2]/div/div[1]/div['
                                              '2]/div/div/div/div/div/strong').text)
            discuss = format_str(browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div[1]/div[2]/div/div['
                                                           '2]/div/div/div[2]/div[2]/button').text)
            answer = format_str(browser.find_element_by_xpath('//*[@id="QuestionAnswers-answers"]/div/div/div/div[1]/h4/span').text)
        except NoSuchElementException:
            break
        else:
            new_info['浏览量'].append(read)
            new_info['评论'].append(discuss)
            new_info['回答'].append(answer)
        comment_button = browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div[1]/div[2]/div/div[2]/div/div/div[2]/div[2]/button')
        comment_button.click()
        time.sleep(3)
        review_info = {'用户名': [], '内容': [], '点赞数': []}
        for j in index_list1:
            try:
                user = browser.find_element_by_xpath(
                    '/html/body/div[4]/div/div/div/div[2]/div/div/div/div/div[2]/ul['+j+']/li/div/div/div[1]/span[2]/a').text
                content = browser.find_element_by_xpath(
                    '/html/body/div[4]/div/div/div/div[2]/div/div/div/div/div[2]/ul['+j+']/li/div/div/div[2]/div[1]/div').text
                like = browser.find_element_by_xpath(
                    '/html/body/div[4]/div/div/div/div[2]/div/div/div/div/div[2]/ul['+j+']/li/div/div/div[2]/div[2]/button[1]').text.replace(
                    '"', '')
                rtime = browser.find_element_by_xpath(
                    '/html/body/div[4]/div/div/div/div[2]/div/div/div/div/div[2]/ul['+j+']/li/div/div/div[1]/span[3]').text
            except NoSuchElementException:
                break
            else:
                review_info['用户名'].append(user)
                review_info['内容'].append(content)
                review_info['点赞数'].append(like)

        print(review_info)
        reviews_info = pd.DataFrame(review_info)
        reviews_info.to_csv('' + convert_list(str(new_info['标题'][i])) + '热评.txt', encoding='utf_8_sig', index=False)
    browser.quit()




parse_review()
news_info = pd.DataFrame(new_info)
news_info.to_csv('5.19知乎热搜.txt', encoding='utf_8_sig', index=False)


