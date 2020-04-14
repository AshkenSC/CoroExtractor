# 从JSON文件中提取并拼接XML

SOURCE = r'F:\Projects\COVID19-kg\source_data\baidu_json\v5'
DEST = r'F:\Projects\COVID19-kg\source_data\baidu_xml\v5'
NAME = 'virus'

import json
import os

source_file = open(os.path.join(SOURCE, NAME+'.json'), 'r', encoding='utf-8')
with open(os.path.join(DEST, NAME+'.xml'), 'w', encoding='utf-8') as dest_file:
    for json_line in source_file:
        line = json.loads(json_line)
        dest_file.write(line['html'])
        print('正在写入：', end='')
        print(line['name'].encode('gbk', 'ignore').decode('gbk'))
source_file.close()

