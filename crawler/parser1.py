#!/bin/usr/python 
#-*- coding:utf8 -*-

import bs4
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote, unquote
from urllib import request
import re, urllib, string
import time

class HtmlParser(object):
    '''解析器'''
    def __init__(self, home='https://baike.baidu.com'):
        self.home = home
        self.header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
        }

    def _get_new_urls(self, soup):
        new_urls = set()
        links = soup.find_all('a', href=re.compile(r"/item/.*?"))
        for link in links:
            new_url = link['href']
            new_full_url = urljoin(self.home, new_url)
            new_full_url = unquote(new_full_url)
            new_full_url=re.split(r'[#\?]', new_full_url)[0]
            new_urls.add(new_full_url)
        return list(new_urls)
    
    def _get_new_data(self, soup, url, html):
        res_data = {}

        # get title
        title = soup.find('dd', class_="lemmaWgt-lemmaTitle-title").find('h1').get_text()
        sub_title = soup.find('dd', class_="lemmaWgt-lemmaTitle-title").find('h2')
        sub_title = sub_title.get_text() if sub_title is not None else ''
        res_data['name'] = title.strip() + sub_title.strip()
        res_data['entity_name'] = unquote(url.strip('https://baike.baidu.com/item/'))

        # 打印显示找到新实体
        #print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), end='\t')
        print(res_data['entity_name'].encode('GBK', 'ignore').decode('GBk'))

        # get summary
        summary_node = soup.find('div', class_="lemma-summary")
        if summary_node is None:
            res_data['summary'] = []
        else:
            summary_para_nodes = summary_node.find_all('div', class_='para')
            summary_paras = paras = [p.get_text().replace('\n', '').strip() for p in summary_para_nodes]
            res_data['summary'] = self._clean_text('\n'.join(summary_paras))

        # get information
        info_node = soup.find('div', class_="basic-info cmn-clearfix")
        # key名与spider中调用的不一致，已更改
        if info_node is None:
            res_data['info'] = []
        else:
            name_nodes = info_node.find_all('dt', class_="basicInfo-item name")
            value_nodes = info_node.find_all('dd', class_="basicInfo-item value")
            assert len(name_nodes) == len(value_nodes), 'Number of names and values are not equal.'
            names = [self._clean_text(name.get_text()).strip() for name in name_nodes]
            values = [value.get_text().strip() for value in value_nodes]
            res_data['info'] = dict(zip(names, values))

        # get contents
        nodes = soup.find_all('div', class_=['para-title level-2', 'para-title level-3', 'para'])
        res_data['contents'] = self._get_contents(nodes)

        # get labels
        res_data['labels'] = []
        labels = soup.find_all('span', class_="taglist")
        for label in labels:
            res_data['labels'].append(label.get_text().strip())

        # get url
        # 对每个实体新增url属性，记录对应百科页面的url
        res_data['url'] = url

        # get html
        res_data['html'] = '\n\n<page>\n' + \
                           '<title>' + res_data['entity_name'] + '</title>\n' + \
                            html + '\n' + \
                            '</page>\n'

        return res_data

    @staticmethod
    def _clean_soup(soup):
        [s.extract() for s in soup.find_all('sup', class_='sup--normal')]
        [s.extract() for s in soup.find_all('a', class_='sup-anchor')]
        [s.extract() for s in soup.find_all('span', class_='title-prefix')]
        [s.extract() for s in soup.find_all('div', class_=re.compile('lemma-picture'))]
        return soup

    @staticmethod
    def _clean_text(text):
        text = re.sub(r'(\u3000|\xa0)', '', text)
        text = re.sub(r'\n+', '\n', text)
        return text

    def _open(self, url):
        req = request.Request(url, headers=self.header)
        response = request.urlopen(req, timeout=30)
        html = response.read().decode('utf8')
        return html

    def _get_contents(self, nodes):
        contents, splits = [], []
        for i, node in enumerate(nodes):
            if node['class'][-1] == 'level-2':
                splits.append(i)
        for i, start in enumerate(splits):
            end = splits[i + 1] if i < len(splits) - 1 else len(nodes)
            title = nodes[start].find('h2', class_='title-text').text.strip()
            has_h3 = any([n['class'][-1] == 'level-3' for n in nodes[start:end]])
            if not has_h3:
                paras = []
                for n in nodes[start:end]:
                    if n['class'][-1] == 'para':
                        paras.append(self._clean_text(n.text.replace('\n', '')).strip())
                content = '\n'.join(paras)
                if len(content) > 100:
                    contents.append({'title': title, 'text': content.strip()})
            else:
                sub_nodes = nodes[start:end]
                _splits = []
                for ii, _node in enumerate(sub_nodes):
                    if _node['class'][-1] == 'level-3':
                        _splits.append(ii)
                for ii, _start in enumerate(_splits):
                    _end = _splits[ii + 1] if ii < len(_splits) - 1 else len(sub_nodes)
                    sub_title = sub_nodes[_start].text.strip()
                    _title = '-'.join([title, sub_title])
                    _paras = []
                    for n in sub_nodes[_start:_end]:
                        if n['class'][-1] == 'para':
                            _paras.append(self._clean_text(n.text.replace('\n', '')).strip())
                    _content = '\n'.join(_paras)
                    if len(_content) > 100:
                        contents.append({'title': _title, 'text': _content.strip()})
        return contents
            

    def parse(self, url):
        url = quote(url, safe=string.printable)
        html = self._open(url)
        soup = BeautifulSoup(html, 'html.parser')
        soup = self._clean_soup(soup)
        new_urls = self._get_new_urls(soup)
        new_data = self._get_new_data(soup, url, html)

        return new_urls, new_data


if __name__ == '__main__':
    import json
    parser = HtmlParser()
    urls = [
        'https://baike.baidu.com/item/%E6%88%90%E8%B4%B5%E9%AB%98%E9%80%9F%E9%93%81%E8%B7%AF',
        'https://baike.baidu.com/item/%E5%B7%9D/1190230',
        'https://baike.baidu.com/item/%E5%84%92%E6%9E%97%E5%A4%96%E5%8F%B2/27018',
        'https://baike.baidu.com/item/%E5%BE%90%E9%94%A1%E9%BA%9F/820817',
        'https://baike.baidu.com/item/%E5%A7%9A%E6%98%8E/28',
        'https://baike.baidu.com/item/%E4%B9%89%E9%A1%B9',
        'https://baike.baidu.com/item/秒懂星课堂',
    ]

    with open('baike.json', 'wb') as fp:
        for url in urls:
            _, data = parser.parse(url)
            line = json.dumps(data, ensure_ascii=False) + '\n'
            fp.write(line.encode('utf8'))
