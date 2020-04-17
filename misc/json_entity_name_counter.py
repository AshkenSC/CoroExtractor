# 统计JSON数据源中有哪些实体名

import json

SOURCE = r'F:\Projects\COVID19-kg\source_data\baidu_json\v5\select_entity_0411.json'
DEST = r'F:\Projects\COVID19-kg\source_data\entity_names\entity_names_v5\select_entity_0411_baidu.txt'

source_file = open(SOURCE, 'r', encoding='utf-8')
with open(DEST, 'w', encoding='utf-8') as dest_file:
    for json_line in source_file:
        line = json.loads(json_line)
        dest_file.write(line['entity_name'] + '\n')
        print(line['entity_name'].encode('gbk', 'ignore').decode('gbk'))
source_file.close()