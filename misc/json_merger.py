# 将JSON合并为一个文件

SOURCE_FOLDER = r'F:\Projects\COVID19-kg\source_data\baidu_json\v5\select_entity_0411'
DEST_FILE = r'F:\Projects\COVID19-kg\source_data\baidu_json\v5\select_entity_0411.json'

import os

file_list = list()  # 保存当前目录下的文件列表
for dir_path, dir_names, file_names in os.walk(SOURCE_FOLDER):
    for file_name in file_names:
        file_list.append(os.path.join(dir_path, file_name))

for file in file_list:
    if file.endswith('.json'):
        print('正在读取文件：' + repr(file).encode('gbk', 'ignore').decode('gbk'))
        with open(os.path.join('', file), 'r', encoding='utf-8') as current_sub_file:
            with open(DEST_FILE, 'a', encoding='utf-8') as output_file:
                for line in current_sub_file:
                    print(line.encode('GBK','ignore').decode('GBk'))
                    output_file.write(line)
