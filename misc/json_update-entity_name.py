# 2020-04-11
# 从JSON中的URL中提取出原始的实体名，从而实现：
# 生成新的实体名单文件
# 添加新的JSON属性：entity_name
# 更新XML，使得<title>中间改为实体名而非网页title

import json
from urllib.parse import unquote
import os
import re

SOURCE_PATH = r'F:\Projects\COVID19-kg\source_data\baidu_json\v3'
NEW_PATH = r'F:\Projects\COVID19-kg\source_data\baidu_json\v5\test'
FILE_NAME = 'disease'

# 实体名单文件
entity_name_file = open(os.path.join('F:\Projects\COVID19-kg\source_data\entity_names\entity_names_v5', FILE_NAME + '.txt'), 'w', encoding='utf-8')

# 原始JSON文件
json_source = open(os.path.join(SOURCE_PATH, FILE_NAME + '.json') , 'r', encoding='utf-8')
# 更新的JSON文件
with open(os.path.join(NEW_PATH, FILE_NAME + '.json'), 'w', encoding='utf-8') as new_json:
    for json_line in json_source:
        line = json.loads(json_line)
        # 新增属性项：实体名
        entity_name = unquote(line['url'].strip('https://baike.baidu.com/item/'))
        line['entity_name'] = entity_name
        # 修改XML
        title_pattern = r'(<title>)(.+)(</title>)'
        old_title = re.search(title_pattern, line['html']).group(2)
        line['html'] = line['html'].replace(old_title, line['entity_name'])
        # 写入新json
        new_json.write(json.dumps(line, ensure_ascii=False) + '\n')
        # 写入实体名单txt
        entity_name_file.write(line['entity_name'] + '\n')

        if line['entity_name'] == '开':
            print('hello')


        print('处理完成：' + line['name'].encode('GBK', 'ignore').decode('GBk'))
json_source.close()
entity_name_file.close()
