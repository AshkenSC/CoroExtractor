# 中文百科
 
## Quick Start

运行脚本开始爬虫：

```shell
python spider.py --worker_num 20 --chunk_size 10000 --log_interval 600 
```

其他参数见--help。参数说明：

| 参数名       | 类型 | 说明                       |
| ------------ | ---- | -------------------------- |
| worker_num   | int  | 爬虫线程数量               |
| chunk_size   | int  | 单位文件样本数量           |
| log_interval | int  | 日志更新间隙               |
| data_dir     | str  | 存储文件目录               |
| log_dir      | str  | 日志目录                   |
| start_url    | str  | 起点url，建议选择热词的url |



## Data Struct

每行一个词条，格式为json字符串，结构为： 

```
{
  "name": "姚明（中国篮球协会主席、中职联公司董事长）",
  "summary": "姚明（Yao Ming），男，汉族，无党派人士...",
  "info": {"身高": "226cm", "祖籍": "苏州吴江",  ......},
  "labels": ["运动员",  "篮球",  ......],
  "contents": [
  		{"title": "职业生涯", "text": "1998年4月，他入选王非执教的国家队..."},
  		{"title": "情感经历", "text": "姚明17岁时第一次见到叶莉..."},
  		......
  	]
} 
```

