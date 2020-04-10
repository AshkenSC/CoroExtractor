import bs4
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote, unquote
from urllib import request
import re, urllib, string
import random 
import telnetlib
import lxml
import json

USER_AGENTS = ["'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)'",
"'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)'",
"'Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)'",
"'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)'",
"'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)'",
"'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)'",
"'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)'",
"'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)'",
"'Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6"'',
"'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1'",
"'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0'",
"'Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5'",
"'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6'",
"'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'",
"'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20'",
"'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52'"]


proxy_data = []



def verify(ip,port,type):
    proxies = {}
    try:
        telnet = telnetlib.Telnet(ip,port=port,timeout=3)
    except:
        print('unconnected')
        return None
    else:
        return 1


with open('verified_proxiesforA+1.json','r') as f:
    i = f.readline()
    proxy_data.append(json.loads(i))
    i = f.readline()
    while(i != ''):
        proxy_data.append(json.loads(i))
        i = f.readline()

def have_next(ele):
    try:
        ele.next()
    except:
        return False
    return True

def is_child(child, father):
    # print(type(father))
    # print(type(child))
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

class HtmlParser(object):
    '''解析器'''
    def __init__(self, home='http://www.a-hospital.com/'):
        self.home = home
        self.header = {'User-Agent':random.choice(USER_AGENTS)}

    def _get_new_urls(self, soup):
        new_urls = set()
        body_contents = soup.find_all('div',id='bodyContent')
        for body_content in body_contents:
            links = body_content.find_all('a')
            for link in links:
                new_url = link['href']
                new_full_url = urljoin(self.home, new_url)
                new_full_url = unquote(new_full_url)
                # new_full_url=re.split(r'[#\?]', new_full_url)[0]
                new_urls.add(new_full_url)
        return list(new_urls)
    
    def _get_new_data(self, html, soup, url):
        res_data = {}

        res_data['pageSource'] = html
        res_data['page_url'] = url
        # get title
        title = soup.find('h1', class_="firstHeading").get_text()
        # sub_title = soup.find('h2', class_="mw-headline")
        # sub_title = sub_title.get_text() if sub_title is not None else ''
        # res_data['name'] = title.strip() + sub_title.strip()
        title_quote = quote(title, safe=string.printable)
        has_h3 = '%E5%88%86%E7%B1%BB:' in title_quote
        if has_h3:
            res_data['name'] = title.strip()
            nameofcategory = str(title.split(':')[1])
            has_subcategories = soup.find('div', id = 'mw-subcategories')
            # if has_subcategories is not None:
            #     subcategories = has_subcategories.find_all('a', class_='CategoryTreeLabelCategory')
            #     category_table = []
            #     with open(r'classtable/class_table_of.json','a') as f1:
            #         for subcategory in subcategories:
            #             category_name = subcategory.get_text()
            #             category_link = subcategory['href']
            #             category_link = urljoin(self.home, category_link)
            #             category_link = unquote(category_link)
            #             category_tabletemp = {'category':title,'subcategory': category_name, 'link': category_link}
            #             category_table.append({'category':title,'subcategory': category_name, 'link': category_link})
            #             lineofcategory = json.dumps(category_tabletemp)+'\n'
            #             print(lineofcategory)
            #             f1.write(lineofcategory)

            has_divsion = soup.find('div', id = 'mw-pages')

            if has_divsion is not None:

                h3 = has_divsion.find_all('h3')
                lengthofh3 = len(h3)
                contents = []
                for i in range(0,lengthofh3-1):
                    incategory = h3[i].get_text()
                    incontent = get_content_between_tables(h3[i], h3[i+1])
                    incontent = incontent.split('\n')[1:]
                    contents.append({'category': incategory, 'content': incontent})
                res_data['contents'] = contents

                detail_list = []
                
                a_list = has_divsion.find_all('a')
                # with open(r'classtable/class_table_ofdetail.json','a') as f2:
                #     for a_detail in a_list:
                #         a_detail_name = a_detail.get_text()
                #         a_detail_link = a_detail['href']
                #         a_detail_link = urljoin(self.home, a_detail_link)
                #         a_detail_link = unquote(a_detail_link)
                #         detail_listtemp = {'category':title,'name':a_detail_name,'link':a_detail_link}
                #         detail_list.append({'category':title,'name':a_detail_name,'link':a_detail_link})
                #         delineofcategory = json.dumps(detail_listtemp)+'\n'
                #         print(delineofcategory)
                #         f2.write(delineofcategory)


                res_data['detail_lists'] = detail_list

                # get labels
                res_data['labels'] = []
                labels = soup.find_all('span', dir="ltr")
                for label in labels:
                    res_data['labels'].append(label.get_text().strip())

        else:
            res_data['name'] = title.strip()


            # get summary
            title = soup.find('table',class_='nav')
            table = soup.find('table',class_='toc')
            summary = get_content_between_tables(title, table)
            if summary is None:
                res_data['summary'] = []
            else:
                summary_paras = summary.replace('\n', '').strip() 
                res_data['summary'] = self._clean_text(''.join(summary_paras))

            div = soup.find_all('h2')
            # lengthofh2 = len(div)

            # # get general table
            # general_table = get_content_between_tables(div[0], div[1])
            
            # # get contents
            # contents = []
            # for i in range(1,lengthofh2-1):
            #     intitle = div[i].get_text()
            #     incontent = get_content_between_tables(div[i], div[i+1])
            #     contents.append({'title': intitle, 'text': incontent.strip()})

            # res_data['contents'] = contents

            # get labels
            res_data['labels'] = []
            labels = soup.find_all('span', dir="ltr")
            for label in labels:
                res_data['labels'].append(label.get_text().strip())

            detail_list = []
            body_contents = soup.find_all('div',id='bodyContent')
            for body_content in body_contents:
                links = body_content.find_all('a')
                for link in links:
                    a_detail_name = link.get_text()
                    a_detail_link = link['href']
                    a_detail_link = urljoin(self.home, a_detail_link)
                    a_detail_link = unquote(a_detail_link)
                    detail_list.append({'name':a_detail_name,'link':a_detail_link})
            res_data['detail_lists'] = detail_list
            
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
        self.header = {'User-Agent':random.choice(USER_AGENTS),'Referer':'http://www.a-hospital.com/w/2019%E6%96%B0%E5%9E%8B%E5%86%A0%E7%8A%B6%E7%97%85%E6%AF%92%E6%84%9F%E6%9F%93%E8%82%BA%E7%82%8E'}
        print(url)
        # ip = random.choice(proxy_data)
        # ipadd = str(ip['host'])
        # ipport = str(ip['port'])
        # ipcp = str(ip['host']) + ':'+str(ip['port'])
        # ipty = str(ip['type'])
        # while (verify(ipadd,ipport,ipty) == None):
        #     ip = random.choice(proxy_data)
        #     ipadd = str(ip['host'])
        #     ipport = str(ip['port'])
        #     ipcp = str(ip['host']) + ':'+str(ip['port'])
        #     ipty = str(ip['type'])

        req = request.Request(url, headers=self.header)
        # req.set_proxy(ipcp, ipty)
        response = request.urlopen(req, timeout=10)


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
        # soup = self._clean_soup(soup)
        new_urls = self._get_new_urls(soup)
        new_data = self._get_new_data(html, soup, url)
        return new_urls, new_data


if __name__ == '__main__':
    import json
    parser = HtmlParser()
    urls = [
            'http://www.a-hospital.com/w/2019%E6%96%B0%E5%9E%8B%E5%86%A0%E7%8A%B6%E7%97%85%E6%AF%92%E6%84%9F%E6%9F%93%E8%82%BA%E7%82%8E',
            'http://www.a-hospital.com/w/%E8%82%BA%E7%82%8E',
            'http://www.a-hospital.com/w/%E7%97%85%E6%AF%92',
            'http://www.a-hospital.com/w/%E5%88%86%E7%B1%BB:%E7%97%85%E6%AF%92',
            'http://www.a-hospital.com/w/%E7%96%BE%E7%97%85',
            'http://www.a-hospital.com/w/%E4%BC%A0%E6%9F%93%E7%97%85',
            ]

    # urls = [
    #         'http://www.a-hospital.com/w/%E5%88%86%E7%B1%BB:%E7%97%85%E6%AF%92'
    #         ]

    urllink = 'http://www.a-hospital.com/w/%E5%88%86%E7%B1%BB:%E7%96%BE%E7%97%85'

    with open('baike.json', 'wb') as fp:
        _, data = parser.parse(urllink)
        print('a')

