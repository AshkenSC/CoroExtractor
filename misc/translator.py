# 将中文三元组翻译为英文
# https://blog.csdn.net/qq_34372112/article/details/98073841

SOURCE = r'F:\Projects\COVID19-kg\source_data\dataset0501\Chinese\infobox_property\baidu\disease_property_value.txt'
DEST = r'F:\Projects\COVID19-kg\source_data\dataset0501\English\infobox_property\baidu\disease_property_value.txt'

from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from retry import retry
import time
import os


chrome_options = Options()

# 隐藏浏览器界面
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(options=chrome_options)


@retry(tries=3, delay=1)
def translate(input, target='en'):
    base_url = 'https://translate.google.cn/#view=home&op=translate&sl=auto&tl=%s' % target

    if browser.current_url != base_url:
        browser.get(base_url)

    submit = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="source"]')))
    submit.clear()
    submit.send_keys(input)
    time.sleep(0.5)
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//span[@class="tlid-translation translation"]')))
    time.sleep(0.5)
    source = etree.HTML(browser.page_source)
    result = source.xpath('//span[@class="tlid-translation translation"]//text()')[0]

    return result


def reformat(string):
    return string.replace(' ;;;; ll ;;;; ', ';;;;ll;;;;')


if __name__ == '__main__':
    # 依次读取文件夹里所有的txt文件
    # 翻译每个txt文件，每次翻译5000字
    # 去除其中的空格，保持原有格式
    # 将翻译结果存入English下对应的文件夹里

    # 读取txt文件
    with open(SOURCE, 'r', encoding='utf-8') as source_file:
        print('源文件打开成功，当前正在翻译: ' + SOURCE)
        # 打开写入文件，分批翻译并写入
        with open(DEST, 'a+', encoding='utf-8') as dest_file:
            lines = source_file.readlines()
            end_line = lines[-1]
            sub_input = ''
            output = ''
            i = 1
            for line in lines:
                print('读取第' + str(i) + '行')
                line = line.strip('\n')
                dest_file.write(reformat(translate(line) + '\n'))
                i += 1
    print('翻译完成。')
    browser.quit()
