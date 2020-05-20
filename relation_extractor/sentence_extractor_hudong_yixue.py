# 从文本中筛选出待预测关系的句子
# 保留 句子 和 两个超链接的名字
# 验证两个超链接名字在不在实体库，都在的才进行预测

# 医学百科和互动版本
# 在处理医学百科数据时，主函数获取网页源代码字段为data['pageSource']
# 在处理互动百科数据时，主函数获取网页源代码字段为data['url']

import json
import re
from urllib.parse import unquote
import bs4
from bs4 import BeautifulSoup
import os

SOURCE = r'f:\Projects\COVID19-kg\source_data\text_sources\hudong\hudong_with_source.json'
DEST = r'F:\Projects\COVID19-kg\output_data\sentences\unformatted\sent_hudong.json'


# 医学百科
def find_relation(page_source, title, entity_list):
    # re.sub(被替换对象的正则表达式，要替换成什么，待处理的字符串）
    #互动百科 <a href='http://www.baike.com/wiki/%E6%81%B6%E6%80%A7%E8%82%BF%E7%98%A4' target='_blank'>恶性肿瘤</a>
    PATTERN1 = r'<a target=_blank href="/item/[a-zA-Z0-9%/-]*" data-lemmaid="[0-9]*">[-+/a-zA-Z0-9\u4e00-\u9fa5]*</a>'
    PATTERN2 = r'<a target=_blank href="/item/[a-zA-Z0-9%/-]*">[-+/a-zA-Z0-9\u4e00-\u9fa5]*</a>'
    page_source = re.sub(title, '<a href="/w/' + title+ '" >'+ title + '</a>', page_source)
    page_source = re.sub('[这其它|他们|它们]', '<a href="/w/' + title+ '" >'+ title + '</a>', page_source)
    html = BeautifulSoup(page_source, 'lxml')
    url = html.find_all('a')    # 未经筛选的URL，包含杂质
    # URL筛选，去掉所有不是词条链接的URL
    # for link in url:
    #     if re.match(PATTERN1, str(link)) is None or re.match(PATTERN2, str(link)) is None:
    #         url.remove(link)
    texts = []
    for i in range(len(url)-1):        #print('test' + str(i))
        txt = get_content_between_tables(url[i], url[i+1])
        reg1 = r'[!。，；：,.?:;\n|、（）<> ]'
        ban = r'百度|百科|隐私|[<>]'   # 筛选头尾禁止出现的关键字
        pattern = re.compile(reg1)
        if len(pattern.findall(txt)) < 1 and \
            len(re.findall(ban, str(url[i].contents))) < 1 and len(re.findall(ban, str(url[i+1].contents))) < 1 and\
            txt != '' and \
            re.match(reg1, txt) is None and \
            url[i].contents != url[i+1].contents:
            if len(url[i].contents) > 0 and len(url[i+1].contents) > 0:
                if '<a' in str(url[i].previousSibling) or '<a' in str(url[i+1].nextSibling):
                    pass
                    #print('yes')
                line = unquote(str(url[i].previous_sibling) + unquote(str(url[i].contents[0])) +  str(txt) + unquote(str(url[i+1].contents[0])) + unquote(str(url[i+1].next_sibling)))
                #if unquote(str(url[i]['href']).split('/w/')[1]) in whole_data or unquote(str(url[i + 1]['href']).split('/w/')[1]) in whole_data:
                head = unquote(str(url[i].contents[0]))
                tail = unquote(str(url[i+1].contents[0]))
                # 判断head和tail是否在实体名单中
                if head_tail_in_entity_list(head, tail, entity_list):
                    line = strip_sentence(line)    # 删除句子中的html标记等杂质
                    texts.append({'sentence': line, 'head': head, 'tail': tail})
                    print('找到句子：' + line.encode('gbk', 'ignore').decode('gbk'))
    return texts


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


# 判断句子中两个url是否在实体名单中
def head_tail_in_entity_list(head, tail, entity_list):
    if head in entity_list and tail in entity_list:
        return True
    else:
        return False


# 载入数据源
def load_source(path):
    with open(path, 'r', encoding='utf-8') as source:
        data = json.loads(source.read())
        return data


def get_title(html):
    title = re.search('(<title>)(.+)(</title>)(\n<!DOCTYPE html)', html).group(2)
    return title


# 载入实体名单
def load_entity_list():
    entity_set = set()
    for root, dirs, files in os.walk(r'f:\Projects\COVID19-kg\source_data\entity_names\entity_names_v6\dataset\entity'):
        for file in files:
            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entity_set.add(line.strip('\n'))
                    except:
                        print('error')
                        print(line.encode('gbk', 'ignore').decode('gbk'))
    return entity_set


# 删除句子中的html标记等杂质
def strip_sentence(string):
    pattern_href = r'(<a href=")(.+)(">)(.*)(</a>)'
    pattern_href_repeat = r'(<a href=")(.+)(">)(.*)(</a>)(\4)'
    pattern_href_2  = r'(<*" href="http://www.baike.com/wiki/)(.+)(">)'
    pattern_inner = r'(<a class="innerlink" href="http://www.baike.com/wiki/)(.+)(" target="_blank" title=")(.+)(">)(.*)(</a>)'
    cnt = 0

    if '尿病酮症酸中毒' in string:
        print('kk')

    while '<a' in string or 'href' in string:
        try:
            if re.search(pattern_href, string) is not None:
                # 处理形如 <a href="/w/乳酸杆菌">乳酸杆菌</a>乳酸杆菌菌种有发
                if re.search(pattern_href_repeat, string) is not None:
                    url_text = re.search(pattern_href, string).group(4)
                    string = re.sub(pattern_href_repeat, url_text, string)
                else:
                    url_text = re.search(pattern_href, string).group(4)
                    string = re.sub(pattern_href, url_text, string)
            if re.search(pattern_inner, string) is not None:
                # 处理形如 <a class="innerlink" href="http://www.baike.com/wiki/间歇热" target="_blank" title="间歇热">间歇热</a>
                url_text = re.search(pattern_inner, string).group(4)
                string = re.sub(pattern_inner, url_text, string)
            if re.search(pattern_href_2, string) is not None:
                # 处理形如 '  糖尿病   糖尿病酮症酸中毒" href="http://www.baike.com/wiki/糖尿病酮症酸中毒">'
                url_text = re.search(pattern_href_2, string).group(4)
                string = re.sub(pattern_href_2, url_text, string)
        except:
            print("error0")
        cnt += 1
        if cnt > 50:
            print('1')
            break

    string = string.strip('[,.!;:，。！；、：（）]').strip('None').strip('<br/>')

    return string


if __name__ == '__main__':
    print(SOURCE)
    sentences_with_entities = list()
    entity_list = load_entity_list()
    with open(SOURCE, 'r', encoding='utf-8') as source:
        while True:
            line = source.readline()
            if line:
                try:
                    data = json.loads(line)
                    title = get_title(data['url'])
                    sentences_with_entities += find_relation(data['url'], title, entity_list)
                except:
                    break
            else:
                break
    with open(DEST, 'w', encoding='utf-8') as output_file:
        output_file.write(json.dumps(sentences_with_entities, ensure_ascii=False, indent=4))
    print('抽取完毕')
