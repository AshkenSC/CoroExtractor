from parser1 import HtmlParser
from utils import Set, Dict
from queue import Queue
from threading import Thread, Timer
from time import sleep, time
import json, os, fire
from urllib.parse import urljoin, quote, unquote

# DATA_DIR为输出JSON目录；NAME_DIR为实体名列表
DATA_DIR = '../source_data/baidu_json/v5/virus'
NAME_DIR = r'type/virus.txt'


# urls = []
# with open('entity.txt','r') as urlf1:
#     a = urlf1.readline().split('\n')[0]
#     urls.append(a)
#     a = urlf1.readline().split('\n')[0]
#     while(a != ''):
#         urls.append(a)
#         a = urlf1.readline().split('\n')[0]

# urls = set(urls)

# catchedurls = []
# with open('catchedentity.txt','r') as urlf2:
#     a = urlf2.readline().split('\n')[0]
#     catchedurls.append(a)
#     a = urlf2.readline().split('\n')[0]
#     while(a != ''):
#         catchedurls.append(a)
#         a = urlf2.readline().split('\n')[0]
    
# catchedurls = set(catchedurls)

# needtocatch = urls - catchedurls


# urls = []
# with open('entity/classification_entity_name.txt','r') as urlf1:
#     a = urlf1.readline().split('\n')[0]
#     urls.append(a)
#     a = urlf1.readline().split('\n')[0]
#     while(a != ''):
#         urls.append(a)
#         a = urlf1.readline().split('\n')[0]

# urls = set(urls)

# catchedurls = []
# with open('entity/catchedentity.txt','r') as urlf2:
#     a = urlf2.readline().split('\n')[0]
#     catchedurls.append(a)
#     a = urlf2.readline().split('\n')[0]
#     while(a != ''):
#         catchedurls.append(a)
#         a = urlf2.readline().split('\n')[0]
    
# catchedurls = set(catchedurls)

# needtocatch = urls - catchedurls
# print(len(needtocatch))


needtocatch = set()
with open(NAME_DIR,'r', encoding='utf-8') as urlf2:
    a = urlf2.readline().split('\n')[0]
    needtocatch.add(a)
    a = urlf2.readline().split('\n')[0]
    while(a != ''):
        needtocatch.add(a)
        a = urlf2.readline().split('\n')[0]
print(len(needtocatch))

# urls = [
#     'http://www.a-hospital.com/w/%E8%82%BA%E7%82%8E',
#     'http://www.a-hospital.com/w/%E7%97%85%E6%AF%92',
#     'http://www.a-hospital.com/w/%E5%88%86%E7%B1%BB:%E7%97%85%E6%AF%92',
#     'http://www.a-hospital.com/w/%E5%88%86%E7%B1%BB:%E4%BC%A0%E6%9F%93%E7%97%85',
#     'http://www.a-hospital.com/w/%E5%88%86%E7%B1%BB:%E5%91%BC%E5%90%B8%E7%B3%BB%E7%BB%9F%E7%96%BE%E7%97%85',
#     'http://www.a-hospital.com/w/%E5%88%86%E7%B1%BB:%E7%BB%86%E8%8F%8C',
#     'http://www.a-hospital.com/w/%E5%88%86%E7%B1%BB:%E8%82%BA%E7%82%8E',
#     'http://www.a-hospital.com/w/%E7%96%BE%E7%97%85',
#     'http://www.a-hospital.com/w/%E4%BC%A0%E6%9F%93%E7%97%85'
#     ]

class Spider(object):
    def __init__(self, worker_num=10, chunk_size=10000, log_interval=600,
                 data_dir='data', log_dir='log'):
        self.chunk_size = chunk_size
        self.log_interval = log_interval
        self.urls = Queue()
        self.results = Queue()
        self.url_cache = Set()
        self.url_cache1 = Set()
        self.url_cache2 = Set()
        self.url_cache3 = Set()
        self.name_cache = Set()
        self.black_urls = Set()
        self.black_cache = Dict()
        self.chunk_num = 0
        self.parser = HtmlParser(home='https://baike.baidu.com')

        self.last = 0
        self.state = 1

        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        self.data_dir = data_dir
        self.log_dir = log_dir

        self.writer = Thread(target=self._write)
        self.logger = Timer(log_interval, self._log)
        self.spiders = [Thread(target=self._scrap) for _ in range(worker_num)]


    def start(self, url):
        if url != '':
            new_urls, new_data = self.parser.parse(url)
            self.results.put(new_data)
            self.url_cache1.add(url)
            self.url_cache.add(url)
            self.name_cache.add(new_data['name'])
        for url1 in needtocatch:
            url1 = str(url1)
            url1 = urljoin('https://baike.baidu.com/item/', url1)
            url1 = unquote(url1)
            self.urls.put(url1)
            self.url_cache1.add(url1)
            self.url_cache.add(url1)
        
        self.logger.start()
        self.writer.start()
        for spider in self.spiders:
            spider.start()
        
    def _write(self):
        """只使用self.results
        """
        while self.state:
            self.chunk_num += 1
            n = 0
            with open(os.path.join(self.data_dir, '{}.json'.format(self.chunk_num)), 'ab') as fp:
                while n < self.chunk_size:
                    if not self.results.empty():
                        result = self.results.get()
                        line = json.dumps(result, ensure_ascii=False) + '\n'
                        fp.write(line.encode('utf8'))
                        n += 1
                    else:
                        sleep(10)

    def _log(self):
        now = len(self.name_cache)
        increase = now - self.last
        self.last = now
        if increase == 0:
            self.state = 1
            #print('Exit: no entities scraped in this round.')
            # exit()
        else:
            with open(os.path.join(self.log_dir, 'log'), 'ab+') as fp:
                message = '新增词条数量：{}，已抓取词条数量：{}；已获取url数量：{}，缓存任务数量：{}，缓存结果数量：{}.'.format(
                    increase, now, len(self.url_cache), self.urls._qsize(), self.results._qsize(),
                ) + '\n'
                fp.write(message.encode('utf8'))
        timer = Timer(self.log_interval, self._log)
        timer.start() 

    def _scrap(self):
        while self.state:
            if not self.urls.empty():
                url = self.urls.get()
                try:
                    new_urls, new_data = self.parser.parse(url)
                except:

                    # print('unable to connnect')
                    self.url_cache.remove(url)
                    # 多次请求不成功的url加入黑名单
                    if url not in self.black_cache:
                        self.black_cache[url] = 1
                    self.black_cache[url] += 1
                    if self.black_cache[url] <= 3:
                        self.urls.put(url)
                    if self.black_cache[url] >= 5:
                        self.black_urls.add(url)
                        print(self.black_urls)
                    continue
                name = new_data['name']
                if name not in self.name_cache:
                    self.name_cache.add(name)
                    self.results.put(new_data)
                # if url in self.url_cache3:
                #     for url in new_urls:
                #         if url not in self.url_cache and url not in self.black_urls:
                #             self.url_cache2.add(url)
                #             self.urls.put(url)   
                # if url in self.url_cache2:
                #     for url in new_urls:
                #         if url not in self.url_cache and url not in self.black_urls:
                #             self.url_cache1.add(url)
                #             self.urls.put(url) 
                sleep(15)

            else:
                sleep(10)


def main(worker_num=20,
         chunk_size=1000,
         log_interval=20,
         data_dir=DATA_DIR,
         log_dir='log',
         start_url=''):
    


    spider = Spider(
        worker_num=worker_num,
        chunk_size=chunk_size,
        log_interval=log_interval,
        data_dir=data_dir,
        log_dir=log_dir,
    )

    spider.start(start_url)


if __name__ == '__main__':
    fire.Fire(main)
