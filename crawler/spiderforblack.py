# -*- coding:utf-8 -*-
from parser1YUAN import HtmlParser
from utils import Set, Dict
from queue import Queue
from urllib.parse import urljoin, quote, unquote
from threading import Thread, Timer
from time import sleep, time
import json, os, fire


urls = [
    'http://www.a-hospital.com/w/%E8%82%BA%E7%82%8E',
    'http://www.a-hospital.com/w/%E7%97%85%E6%AF%92',
    'http://www.a-hospital.com/w/%E5%88%86%E7%B1%BB:%E7%97%85%E6%AF%92',
    'http://www.a-hospital.com/w/%E5%88%86%E7%B1%BB:%E4%BC%A0%E6%9F%93%E7%97%85',
    'http://www.a-hospital.com/w/%E5%88%86%E7%B1%BB:%E5%91%BC%E5%90%B8%E7%B3%BB%E7%BB%9F%E7%96%BE%E7%97%85',
    'http://www.a-hospital.com/w/%E5%88%86%E7%B1%BB:%E7%BB%86%E8%8F%8C',
    'http://www.a-hospital.com/w/%E5%88%86%E7%B1%BB:%E8%82%BA%E7%82%8E',
    'http://www.a-hospital.com/w/%E7%96%BE%E7%97%85',
    'http://www.a-hospital.com/w/%E4%BC%A0%E6%9F%93%E7%97%85'
    ]

blackset = set({'http://www.a-hospital.com/w/特殊:页面分类', 'http://www.a-hospital.com/w/性纤毛', 'http://www.a-hospital.com/w/肺风', 'http://www.a-hospital.com/w/嗜盐菌', 'http://www.a-hospital.com/w/紫外线', 'http://www.a-hospital.com/index.php?title=出汗&action=edit&redlink=1', 'http://www.a-hospital.com/w/阴道炎局部用药', 'http://www.a-hospital.com/w/肺泡', 'http://www.a-hospital.com/#.E7.BD.95.E8.A7.81.E7.97.87.E7.8A.B6', 'http://www.a-hospital.com/index.php?title=偏头疼&action=edit&redlink=1', 'http://www.a-hospital.com/index.php?title=卡氏肺囊虫性肺炎&action=edit&redlink=1', 'http://www.a-hospital.com/w/肠杆菌科', 'http://www.a-hospital.com/w/医疗康复/肺炎', 'http://www.a-hospital.com/index.php?title=肺泡性肺炎&action=edit&redlink=1', 'http://www.a-hospital.com/w/银花', 'http://www.a-hospital.com/index.php?title=全身疲惫&action=edit&redlink=1', 'http://www.a-hospital.com/w/复壮', 'http://www.a-hospital.com/w/革兰氏染色法', 'http://www.a-hospital.com/index.php?title=呼吸衰竭综合症&action=edit&redlink=1', 'http://www.a-hospital.com/w/肝炎', 'http://www.a-hospital.com/w/弯曲菌属', 'http://www.a-hospital.com/index.php?title=肉芽肿性肺炎&action=edit&redlink=1', 'http://www.a-hospital.com/w/硫细菌', 'http://www.a-hospital.com/index.php?title=风湿性肺炎&action=edit&redlink=1', 'http://www.a-hospital.com/w/着色芽生菌病', 'http://www.a-hospital.com/w/人感染高致病性禽流感', 'http://www.a-hospital.com/#.E4.B8.AD.E5.8C.BB', 'http://www.a-hospital.com/w/气短', 'http://www.a-hospital.com/index.php?title=讨论:肺炎&feed=rss&action=history', 'http://www.a-hospital.com/w/伤阴', 'http://www.a-hospital.com/w/病理学/肺炎', 'http://www.a-hospital.com/w/生津', 'http://www.a-hospital.com/w/牙龈炎', 'http://www.a-hospital.com/w/固氮菌', 'http://www.a-hospital.com/w/%E4%BC%A0%E6%9F%93%E7%97%85', 'http://www.a-hospital.com/index.php?title=血液检查&action=edit&redlink=1', 'http://www.a-hospital.com/w/咳血', 'http://www.a-hospital.com/w/变质性炎症', 'http://www.a-hospital.com/#p-search', 'http://www.a-hospital.com/w/弧菌', 'http://www.a-hospital.com/w/粉尘螨', 'http://www.a-hospital.com/w/芥子气', 'http://www.a-hospital.com/w/角膜炎', 'http://www.a-hospital.com/w/葡萄球菌', 'http://www.a-hospital.com/index.php?title=闭塞性细支气管炎伴机化性肺炎&action=edit&redlink=1', 'http://www.a-hospital.com/w/变形杆菌属', 'http://www.a-hospital.com/w/姜片虫病', 'http://www.a-hospital.com/w/霉菌性肺炎', 'http://www.a-hospital.com/w/棒状杆菌', 'http://www.a-hospital.com/#.E5.88.86.E7.B1.BB', 'http://www.a-hospital.com/w/抗溃疡性结肠炎药', 'http://www.a-hospital.com/index.php?title=化脓性肺炎&action=edit&redlink=1', 'http://www.a-hospital.com/w/痰喘', 'http://www.a-hospital.com/w/天花', 'http://www.a-hospital.com/w/肺段', 'http://www.a-hospital.com/#.E8.AF.8A.E6.96.AD', 'http://www.a-hospital.com/w/流行病学', 'http://www.a-hospital.com/index.php?title=祛痰平喘&action=edit&redlink=1', 'http://www.a-hospital.com/w/鸟分枝杆菌', 'http://www.a-hospital.com/w/鞭毛蛋白', 'http://www.a-hospital.com/index.php?title=浆液性肺炎&action=edit&redlink=1', 'http://www.a-hospital.com/w/甲沟炎', 'http://www.a-hospital.com/index.php?title=嗜血流感杆菌&action=edit&redlink=1', 'http://www.a-hospital.com/index.php?title=免疫不全&action=edit&redlink=1', 'http://www.a-hospital.com/index.php?title=讨论:肺炎&action=edit&section=new&preload=模板:签名&editintro=模板:签名说明&preloadtitle=给肺炎条目的留言', 'http://www.a-hospital.com/w/家庭诊疗/肺炎', 'http://www.a-hospital.com/w/双球菌', 'http://www.a-hospital.com/w/呼吸病学/肺炎', 'http://www.a-hospital.com/w/喘咳', 'http://www.a-hospital.com/w/呼吸急促', 'http://www.a-hospital.com/w/医学影像学/肺炎', 'http://www.a-hospital.com/w/模板:导航板-细菌', 'http://www.a-hospital.com/w/理化性肺炎', 'http://www.a-hospital.com/w/登革热', 'http://www.a-hospital.com/w/棒状杆菌属', 'http://www.a-hospital.com/w/首页', 'http://www.a-hospital.com/w/疏风', 'http://www.a-hospital.com/#.E7.97.87.E7.8A.B6', 'http://www.a-hospital.com/index.php?title=肉状瘤病&action=edit&redlink=1', 'http://www.a-hospital.com/#mw-head', 'http://www.a-hospital.com/w/衣原体肺炎', 'http://www.a-hospital.com/w/抗生素', 'http://www.a-hospital.com/w/血管炎', 'http://www.a-hospital.com/#.E5.8F.82.E7.9C.8B', 'http://www.a-hospital.com/#.E6.B2.BB.E7.96.97', 'http://www.a-hospital.com/w/菌落', 'http://www.a-hospital.com/w/奈瑟氏菌', 'http://www.a-hospital.com/index.php?title=出血性肺炎&action=edit&redlink=1', 'http://www.a-hospital.com/w/三黄石膏汤', 'http://www.a-hospital.com/w/浸润', 'http://www.a-hospital.com/', 'http://www.a-hospital.com/#.E5.B8.B8.E8.A7.81.E7.97.87.E7.8A.B6', 'http://www.a-hospital.com/w/脊髓灰质炎', 'http://www.a-hospital.com/w/条件致病菌', 'http://www.a-hospital.com/index.php?title=抗尿激素&action=edit&redlink=1', 'http://www.a-hospital.com/index.php?title=变态反应性肺炎&action=edit&redlink=1', 'http://www.a-hospital.com/w/畏寒', 'http://www.a-hospital.com/index.php?title=纤维素性肺炎&action=edit&redlink=1', 'http://www.a-hospital.com/w/抑菌剂', 'http://www.a-hospital.com/w/假单胞菌', 'http://www.a-hospital.com/w/头孢氨苄', 'http://www.a-hospital.com/w/腐生菌', 'http://www.a-hospital.com/index.php?title=节段性肺炎&action=edit&redlink=1', 'http://www.a-hospital.com/w/放射诊断/肺炎', 'http://www.a-hospital.com/w/猩红热', 'http://www.a-hospital.com/w/化脓性炎', 'http://www.a-hospital.com/index.php?title=大叶&action=edit&redlink=1', 'http://www.a-hospital.com/w/纤维素性炎', 'http://www.a-hospital.com/w/鼻病毒', 'http://www.a-hospital.com/w/四联球菌', 'http://www.a-hospital.com/#.E5.B8.B8.E8.A7.81.E8.82.BA.E7.82.8E', 'http://www.a-hospital.com/index.php?title=干酪性肺炎&action=edit&redlink=1'})

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
        self.parser = HtmlParser(home='http://www.a-hospital.com/')

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
        new_urls, new_data = self.parser.parse(url)
        self.results.put(new_data)
        self.url_cache1.add(url)
        self.url_cache.add(url)
        self.name_cache.add(new_data['name'])
        lenofblackset = len(blackset)
        for i in range(lenofblackset):
            data111 = blackset.pop()
            self.urls.put(data111)
            self.url_cache1.add(data111)
        # for url2 in new_urls:
        #     self.urls.put(url2)
        
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
            with open(os.path.join(self.data_dir, '{}.json'.format(self.chunk_num)), 'wb') as fp:
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
            print('Exit: no entities scraped in this round.')
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
                    
                    print('unable to connnect')
                    self.url_cache.remove(url)
                    # 多次请求不成功的url加入黑名单
                    if url not in self.black_cache:
                        self.black_cache[url] = 1
                    self.black_cache[url] += 1
                    if self.black_cache[url] >= 10:
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
                # if url in self.url_cache1:
                #     for url in new_urls:
                #         if url not in self.url_cache and url not in self.black_urls:
                #             self.urls.put(url) 
                #             self.url_cache.add(url)
                sleep(3)

            else:
                sleep(10)


def main(worker_num=20,
         chunk_size=10000,
         log_interval=20,
         data_dir='data',
         log_dir='log',
         start_url='http://www.a-hospital.com/w/%E8%82%BA%E7%82%8E'):
    

    urls = [
        'http://www.a-hospital.com/w/2019%E6%96%B0%E5%9E%8B%E5%86%A0%E7%8A%B6%E7%97%85%E6%AF%92%E6%84%9F%E6%9F%93%E8%82%BA%E7%82%8E',
        'http://www.a-hospital.com/w/%E8%82%BA%E7%82%8E',
        'http://www.a-hospital.com/w/%E7%97%85%E6%AF%92',
        'http://www.a-hospital.com/w/%E5%88%86%E7%B1%BB:%E7%97%85%E6%AF%92',
        'http://www.a-hospital.com/w/%E5%88%86%E7%B1%BB:%E4%BC%A0%E6%9F%93%E7%97%85',
        'http://www.a-hospital.com/w/%E5%88%86%E7%B1%BB:%E5%91%BC%E5%90%B8%E7%B3%BB%E7%BB%9F%E7%96%BE%E7%97%85',
        'http://www.a-hospital.com/w/%E5%88%86%E7%B1%BB:%E7%BB%86%E8%8F%8C',
        'http://www.a-hospital.com/w/%E5%88%86%E7%B1%BB:%E8%82%BA%E7%82%8E',
        'http://www.a-hospital.com/w/%E7%96%BE%E7%97%85',
        'http://www.a-hospital.com/w/%E4%BC%A0%E6%9F%93%E7%97%85'
        ]
    
    spider = Spider(
        worker_num=worker_num,
        chunk_size=chunk_size,
        log_interval=log_interval,
        data_dir=data_dir,
        log_dir=log_dir,
    )

    for start_url1 in urls:
        spider.start(start_url1)


if __name__ == '__main__':
    fire.Fire(main)
