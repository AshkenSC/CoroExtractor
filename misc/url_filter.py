# 读取实体名单，筛选出url不能访问的实体名

from bs4 import BeautifulSoup
from urllib import request
from urllib.parse import quote
import os

SOURCE_NAME = 'symptom.txt'
header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
        }

print(SOURCE_NAME)
name_file = open(os.path.join(r'F:\Projects\COVID19-kg\crawler\type', SOURCE_NAME), 'r', encoding='utf-8')
with open(os.path.join(r'C:\Users\ASUS\Desktop\name_v0411', SOURCE_NAME), 'w', encoding='utf-8') as output:
    for name in name_file:
        url = 'https://baike.baidu.com/item/' + quote(name.strip('\n'))
        try:
            req = request.Request(url, headers=header)
            response = request.urlopen(req, timeout=30)
            if response.url != 'https://baike.baidu.com/error.html':
                print(name.encode('GBK', 'ignore').decode('GBk'))
                output.write(name + '\n')
            else:
                print('error: ' + name.encode('GBK', 'ignore').decode('GBk'))
        except:
            print('error: ' + name.encode('GBK', 'ignore').decode('GBk'))
name_file.close()