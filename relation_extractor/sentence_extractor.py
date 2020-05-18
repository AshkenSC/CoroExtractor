# 从文本中筛选出待预测关系的句子
# 保留 句子 和 两个超链接的名字
# 验证两个超链接名字在不在实体库，都在的才进行预测

import re
from urllib.parse import unquote
import bs4

from bs4 import BeautifulSoup


# 百度
# TODO: 整合互动和医学
def find_relation(page_source, title):
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


# 用于替换别名
def sub_alias(title, page):
    if title in aliases.keys():
        if len(aliases[title]) > 0:
            for alias in aliases[title]:
                print('替换别名：' + alias.encode('gbk', 'ignore').decode('gbk') + ' --> ' + title.encode('gbk', 'ignore').decode('gbk'))
                page = re.sub(alias, '<a href="/w/' + title + '" >' + title + '</a>', page)
    return page


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