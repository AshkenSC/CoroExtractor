# 将备查句子转化为三元组的格式

SOURCE = r'f:\Projects\corona\baidu_data\sentences\to_check\inspect_to_check.txt'
DEST = r'f:\Projects\corona\hudong_data\rough_triples\NER_rough_triples_baidu_inspect.txt'
KEY_EN = ' inspect '
KEY_CN = '检查'

source_file = open(SOURCE, 'r', encoding='utf-8')
with open(DEST, 'w', encoding='utf-8') as output_file:
    for line in source_file:
        triple = line.split(KEY_EN)
        if len(triple) == 2:
            output_file.write(triple[0] + ';;;;ll;;;;' + KEY_CN + ';;;;ll;;;;' + triple[1])
            print((triple[0] + KEY_CN + triple[1]).encode('gbk', 'ignore').decode('gbk'))
source_file.close()