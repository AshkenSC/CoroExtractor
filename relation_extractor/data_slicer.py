# 将待预测数据进行切分，便于模型载入

import json

SOURCE = r'f:\Projects\COVID19-kg\output_data\sentences\formatted\formatted_sentences.json'
DEST = r'f:\Projects\COVID19-kg\output_data\sentences\formatted'
SUB_SIZE = 10000

with open(SOURCE, 'r', encoding='utf-8') as source_file:
    data = json.loads(source_file.read())
    i = 0
    j = 0
    exit_flag = False
    while i <= len(data):
        j += SUB_SIZE
        if len(data) < j:
            j = len(data)
            exit_flag = True
        sub_data = list()
        while i < j:
            sub_data.append(data[i])
            i += 1
        with open(DEST + '\\' + str(int(j / SUB_SIZE)) + '.json', 'w', encoding='utf-8') as out_file:
            out_file.write(json.dumps(sub_data, ensure_ascii=False, indent=4))
            print('写入子文件' + str(int(j / SUB_SIZE)))
        if exit_flag:
            break

