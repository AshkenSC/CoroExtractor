# 初步提取超链接和两个超链接之间的文本。
# 下一步根据链接间文本生成ngram，并根据关系关键字对文本做筛选

SOURCE_PATH = r'D:\Project\Python\PythonGadgets\web_crawler\baike_spider-master\classified-merged\classified-merged-json\v2'
DEST_PATH = r'F:\Projects\COVID19-kg\output_data\classless_relations\link\raw_relations'

from bs4 import BeautifulSoup
import bs4
import lxml
import os
import re
import json
from urllib.parse import urljoin, quote, unquote
from os.path import join

# 载入实体名集合
entity_name_set = set()
with open(r'F:\Projects\COVID19-kg\entity_classless_relation_extractor\total_entity.txt', 'r', encoding='utf-8') as entity_name_file:
    for line in entity_name_file:
        entity_name_set.add(line.strip('\n'))
print('实体名集合载入完成。')

ngrams = dict()

for i in range(0,50):
    ngrams[i] = dict()

# 载入别名文件
alias_source = open(r'D:\Project\Python\PythonGadgets\web_crawler\baike_spider-master\alias\alias.json', 'r', encoding='utf-8')
aliases = dict()
for json_line in alias_source:
    line = json.loads(json_line)
    for entry in line.items():
        aliases[entry[0]] = entry[1]
alias_source.close()

# 用于替换别名
def sub_alias(title, page):
    if title in aliases.keys():
        if len(aliases[title]) > 0:
            for alias in aliases[title]:
                print('替换别名：' + alias.encode('gbk', 'ignore').decode('gbk') + ' --> ' + title.encode('gbk', 'ignore').decode('gbk'))
                page = re.sub(alias, '<a href="/w/' + title + '" >' + title + '</a>', page)
    return page

def have_next(ele):
    try:
        ele.next()
    except:
        return False
    return True

def is_child(child, father):
    if child in father:
        return True
    seek_list = father.contents
    for i in seek_list:
        if isinstance(i, bs4.element.NavigableString):
            pass
        elif child in i:
            return True
        else:
            flag = is_child(child, i)
            if flag == True:
                return True
    return False

def get_content_between_tables(pre, nxt):
    #如果第二个table在第一个里面
    txt = ""
    if is_child(nxt, pre):
        cur = pre.next_element
        while cur != nxt and cur is not None:
            if isinstance(cur, bs4.element.NavigableString):
                txt += cur
            cur = cur.next_element
    #类似并列关系
    else:
        #先找到pre结束的下一个元素
        cur = pre.next_element
        while is_child(cur, pre):
            cur = cur.next_element
        #获取内容
        while cur != nxt and cur is not None:
            if isinstance(cur, bs4.element.NavigableString):
                txt += cur
            cur = cur.next_element
    return txt

def findrelation(page_source, title):
    # re.sub(被替换对象的正则表达式，要替换成什么，待处理的字符串）
    #互动百科 <a href='http://www.baike.com/wiki/%E6%81%B6%E6%80%A7%E8%82%BF%E7%98%A4' target='_blank'>恶性肿瘤</a>
    PATTERN1 = r'<a target=_blank href="/item/[a-zA-Z0-9%/-]*" data-lemmaid="[0-9]*">[-+/a-zA-Z0-9\u4e00-\u9fa5]*</a>'
    PATTERN2 = r'<a target=_blank href="/item/[a-zA-Z0-9%/-]*">[-+/a-zA-Z0-9\u4e00-\u9fa5]*</a>'
    page_source = re.sub(title, '<a href="/w/' + title+ '" >'+ title + '</a>', page_source)
    page_source = re.sub('[这其它|他们|它们]', '<a href="/w/' + title+ '" >'+ title + '</a>', page_source)
    page_source = sub_alias(title, page_source)  # 将网页里的别名替换
    html = BeautifulSoup(page_source, 'lxml')
    url = html.find_all('a')    # 未经筛选的URL，包含杂质
    # URL筛选，去掉所有不是词条链接的URL
    # for link in url:
    #     if re.match(PATTERN1, str(link)) is None or re.match(PATTERN2, str(link)) is None:
    #         url.remove(link)
    texts = []
    for i in range(len(url)-1):
        txt = get_content_between_tables(url[i], url[i+1])
        reg1 = r'[!。，；：,.?:;\n|、（）<> ]'
        ban = r'百度|百科|隐私|[<>]'   # 筛选头尾禁止出现的关键字
        pattern = re.compile(reg1)
        if len(pattern.findall(txt)) < 1 and \
            len(re.findall(ban, str(url[i].contents))) < 1 and len(re.findall(ban, str(url[i+1].contents))) < 1 and\
            txt != '' and \
            re.match(reg1, txt) is None and \
            url[i].contents != url[i+1].contents:
            if len(url[i].contents)>0 and len(url[i+1].contents)>0:
                line = unquote(str(url[i].contents[0])) +  ';;;;ll;;;;' + unquote(str(url[i+1].contents[0])) + ';;;;ll;;;;' + str(txt)
                #if unquote(str(url[i]['href']).split('/w/')[1]) in whole_data or unquote(str(url[i + 1]['href']).split('/w/')[1]) in whole_data:
                texts.append(line)
                print('找到关系：' + line.encode('gbk', 'ignore').decode('gbk'))
    return texts

files = os.listdir(SOURCE_PATH)[:]
output_file = open(join(DEST_PATH, 'raw_triples.txt'), 'w', encoding='utf-8')
for file in files:
    with open(os.path.join(SOURCE_PATH, file), 'r', encoding='utf-8') as f:
        i = f.readline()
        # print(single_file)
        data = json.loads(i, strict=False)
        title = data['name']
        if 'html' in data.keys():
            page_source = data['html']
            lines = findrelation(page_source, title.encode('gbk', 'ignore').decode('gbk'))
            if title in entity_name_set:
                #fp1.write(title + '\n')
                if len(lines) > 0:
                    for i in lines:
                        output_file.write(str(i) + '\n')
            i = f.readline()
        while i != '':
            data = json.loads(i, strict=False)
            title = data['name']
            if 'html' in data.keys():
                page_source = data['html']
                lines = findrelation(page_source, title)
                if title in entity_name_set:
                    if len(lines) > 0:
                        for i in lines:
                            output_file.write(str(i) + '\n')
            i = f.readline()
output_file.close()

