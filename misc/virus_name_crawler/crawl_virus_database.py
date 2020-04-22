from bs4 import BeautifulSoup
import time
import os
import re
from crawl_utils import sep
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait


def normal_word(word):
    reg = "^[0-9 :]*"
    return re.sub(reg, '', word)
# 爬取病毒资源数据库所有实体
# http://virus.micro.csdb.cn/vri.jsp

category_list = ['动物病毒', '医学病毒', '植物病毒', '昆虫病毒', '细菌病毒']

def get_entity(content, category):
    vdf = open(os.path.join('../data/virus_names_in_database', 'virus_database_entity_type.txt'), 'a', encoding='utf-8')
    soup = BeautifulSoup(content, 'html.parser')
    div_list = soup.findAll('div', {'class': 'panel panel-default ng-scope'})
    for div in div_list:
        name = normal_word(div.find('div',{'class': 'panel-heading ng-binding'}).get_text())
        type = category
        vdf.write(name + sep + 'type' + sep + type + '\n')
    vdf.close()

def distinct():
    triples = set()
    vrf = open(os.path.join('../data/virus_names_in_database', 'virus_database_entity_type.txt'), 'r', encoding='utf-8')
    for line in vrf:
        if line and line.strip():
            triples.add(line)
    vrf.close()

    vwf = open(os.path.join('../data/virus_names_in_database', 'virus_database_entity_type.txt'), 'w', encoding='utf-8')
    for triple in triples:
        vwf.write(triple)
    vwf.close()

if __name__ == '__main__':
    browser = webdriver.Chrome(executable_path=r'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')
    browser.maximize_window()
    browser.get('http://virus.micro.csdb.cn/vri.jsp')
    wait = WebDriverWait(browser, 10)
    for category in category_list:
        button = browser.find_element_by_xpath("//*[text() = '"+category+"']")
        button.click()
        current_page = 1
        get_entity(browser.page_source, category)
        # 翻页
        while True:
            time.sleep(0.5)
            next_button = browser.find_element_by_xpath("//*[text() = '»']")
            next_button.click()
            time.sleep(0.5)
            next_page = browser.find_element_by_xpath('//li[@class="ng-scope active"]').text
            # 到达最后一页
            if str(current_page) == next_page:
                break
            current_page = next_page
            get_entity(browser.page_source, category)
    distinct()



