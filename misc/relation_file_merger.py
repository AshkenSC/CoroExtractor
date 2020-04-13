# 将同一个文件夹下的所有关系三元组文件合并到一个文件中，并去重

# 数据源文件夹
FOLDER_PATH = r'f:\Projects\COVID19-kg\output_data\infobox_triples_baidu'
# 合并后存放文件
DEST_FILE = r'f:\Projects\COVID19-kg\output_data\infobox_triples_baidu\infobox_triples_baidu_merged.txt'

import os

data1 = set()

def readtoset(file,data123,file1):
    f = file
    i = f.readline()
    if i not in data123:
        data123.add(i)
        f3.write(i)
    i = f.readline()
    while(i != ''):
        if i not in data123:
            data123.add(i)
            f3.write(i)
        i = f.readline()

file_list = list()  # 保存当前目录下的文件列表
for dir_path, dir_names, file_names in os.walk(FOLDER_PATH):
    for file_name in file_names:
        file_list.append(os.path.join(dir_path, file_name))

for file in file_list:
    if file.endswith('.txt'):
        print('正在读取文件：' + repr(file).encode('gbk', 'ignore').decode('gbk'))
        with open(os.path.join('', file), 'r', encoding='utf-8') as f1:
            with open(DEST_FILE, 'a', encoding='utf-8') as f3:
                readtoset(f1,data1,f3)
