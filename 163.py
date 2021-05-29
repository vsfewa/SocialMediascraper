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
    return str.replace('[', '').replace(']', '').replace('\'', '').replace('"','')


new_info = {'序号': [], '标题': [], '跟帖': [], '评论数': []}
link = {'序号': [], '用户名': []}
headers = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.114 Safari/537.36',
    'Cookie': '_ntes_nnid=7c91e0693f4645a5e332ca939361772f,1618472856431; pver_n_f_l_n3=a; '
              '_ntes_nuid=7c91e0693f4645a5e332ca939361772f; UserProvince=%u5168%u56FD; '
              'ne_analysis_trace_id=1619006180864; _antanalysis_s_id=1619006197034; '
              's_n_f_l_n3=c203ceca9e97f1701619008563199; '
              'NTES_SESS=ZqagmdDRdRrAOWZxZ0u3tPC9izyUiA4G_DNJVnJyGeebGTk4G2l_fIVMusuz3W0'
              '.BZabQxm2GnKEzXdUSYxOfQ4milwp3YSddnSZZ9iiTN4G0ZpLvYqoIBpj2O7ouh4dozJOtPBegvXKK4qm'
              '.ZdsCas2fvRJEmPfYmNExKIGrobTOwxM1UYvU2ijPCzsY3fQuep8fk7MrdTxI; S_INFO=1619008667|0|3&80##|fsfqqq; '
              'P_INFO=fsfqqq@163.com|1619008667|0|unireg|00&99|null&null&null#zhj&330100#10#0#0|&0||fsfqqq@163.com; '
              'cm_newmsg=user%3Dfsfqqq%40163.com%26new%3D1%26total%3D1; '
              'NTES_CMT_USER_INFO=310737580%7C%E6%9C%89%E6%80%81%E5%BA%A6%E7%BD%91%E5%8F%8B0ixnGI%7Chttp%3A%2F%2Fcms'
              '-bucket.nosdn.127.net%2F2018%2F08%2F13%2F078ea9f65d954410b62a52ac773875a1.jpeg%7Cfalse'
              '%7CZnNmcXFxQDE2My5jb20%3D; vinfo_n_f_l_n3=c203ceca9e97f170.1.15.1618472887015.1619007404045'
              '.1619008745769 '
}
url = 'https://news.163.com/domestic/'  # 需要爬数据的网址
page = requests.Session().get(url, headers=headers)
tree = html.fromstring(page.text)
pre = 'https://www.163.com/news/article/'
cookie_path = 'D:\\cookies\\163cookies.txt'
url_list = []
index_list1 = ['1', '2', '3', '4', '5', '6', '7']
index_list2 = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
k = 15
for i in index_list1:
    title = tree.xpath('/html/body/div/div[3]/div[3]/div[2]/ul/li[' + i + ']/a/text()')
    url = tree.xpath('/html/body/div/div[3]/div[3]/div[2]/ul/li[' + i + ']/a/@href')
    new_info['序号'].append(k)
    k = k + 1
    new_info['标题'].append(title)  # 获取需要的数据
    url_list.append(url)


# 动态加载网页使用selenium
def parse_review():
    for i in range(0, 7):
        new_url = convert_list(str(url_list[i])).replace(pre, '')
        new_url = 'https://comment.tie.163.com/' + new_url
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
        tiezi = browser.find_element_by_xpath('//*[@id="tie-main"]/div[2]/div[1]/div[1]/span/em[1]').text
        discuss = browser.find_element_by_xpath('//*[@id="tie-main"]/div[2]/div[1]/div[1]/span/em[2]').text
        new_info['跟帖'].append(tiezi)
        new_info['评论数'].append(discuss)
        review_info = {'用户名': [], '内容': [], '点赞数': []}
        for j in index_list2:
            try:
                user = browser.find_element_by_xpath(
                    '//*[@id="tie-main"]/div[2]/div[2]/div[1]/div[' + j + ']/div[2]/div[1]/div[1]/a').text
            except NoSuchElementException:

                review_info['用户名'].append('匿名')
            else:
                review_info['用户名'].append(user)
                link['用户名'].append(user)
                link['序号'].append(convert_list(str(new_info['序号'][i])))
            try:
                content = browser.find_element_by_xpath(
                    '//*[@id="tie-main"]/div[2]/div[2]/div[1]/div[' + j + ']/div[2]/div[2]/div/p').text
                like = browser.find_element_by_xpath(
                    '//*[@id="tie-main"]/div[2]/div[2]/div[1]/div[' + j + ']/div[2]/div[3]/div/ul[1]/li[1]/span/em').text.replace(
                    '[', '').replace(']', '')
                rtime = browser.find_element_by_xpath(
                    '//*[@id="tie-main"]/div[2]/div[2]/div[1]/div[' + j + ']/div[2]/div[1]/div[2]/span[2]').text
            except NoSuchElementException:
                review_info['用户名'].pop()
                link['用户名'].pop()
                break
            else:
                review_info['内容'].append(content)
                review_info['点赞数'].append(like)


        print(review_info)
        reviews_info = pd.DataFrame(review_info)
        reviews_info.to_csv('' + convert_list(str(new_info['标题'][i])) + '热评.txt', encoding='utf_8_sig', index=False)
        browser.close()
    browser.quit()


parse_review()
news_info = pd.DataFrame(new_info)
news_info.to_csv('5.19网易推荐新闻.txt', encoding='utf_8_sig', index=False)
#
# link_info = pd.DataFrame(link)
# link_info.to_csv('link3.txt', encoding='utf_8_sig', index=False)

