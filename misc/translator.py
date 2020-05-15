# 将中文三元组翻译为英文
# https://blog.csdn.net/qq_34372112/article/details/98073841

SOURCE = r'F:\Projects\COVID19-kg\source_data\dataset0501\Chinese\infobox_property\baidu\bacteria_property_value.txt'
DEST = r'F:\Projects\COVID19-kg\source_data\dataset0501\English\infobox_property\baidu\bacteria_property_value.txt'

from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from retry import retry


chrome_options = Options()

# 隐藏浏览器界面
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(options=chrome_options)


@retry(tries=3, delay=1)
def translate(input, target):
    base_url = 'https://translate.google.cn/#view=home&op=translate&sl=auto&tl=%s' % target

    if browser.current_url != base_url:
        browser.get(base_url)

    submit = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="source"]')))
    submit.clear()
    submit.send_keys(input)
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//span[@class="tlid-translation translation"]')))
    source = etree.HTML(browser.page_source)
    result = source.xpath('//span[@class="tlid-translation translation"]//text()')[0]

    return result


if __name__ == '__main__':
    for i in range(100):
        print(translate('中英翻译测试', target='en'))
        print(translate('再测试一下', target='en'))
        print(translate('hello world', target='zh-CN'))
    browser.quit()
