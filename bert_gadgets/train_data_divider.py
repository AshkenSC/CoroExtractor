# 将同一目录下的所有deepke训练数据条目文件整合后，按一定比例划分为train，test，valid

import os

PATH = r"F:\Projects\deepke-master\data\origin" # 文件夹名称
TRAIN = 3.0; TEST = 1.0; VALID = 1.0            # 数据集划分比例

# 读取文件
file_list = list()
for i in os.listdir(PATH):                      #遍历整个文件夹
    path = os.path.join(PATH, i)
    if os.path.isfile(path):                    #判断是否为一个文件，排除文件夹
        if os.path.splitext(path)[1] == ".txt":  #判断文件扩展名是否为指定扩展名
            file_list.append(open(os.path.join(PATH, i), 'r', encoding='utf-8'))


# 将所有条目载入集合
entry_set = set()
for file in file_list:
    for line in file:
        entry_set.add(line)

# 划分数据集
train_set = set()
train_size = int(len(entry_set) * TRAIN / (TRAIN + VALID + TEST))
test_set = set()
test_size = int(len(entry_set) * TEST / (TRAIN + VALID + TEST))
valid_set = set()
valid_size = len(entry_set) - train_size - test_size
for i in range(train_size):
    train_set.add(entry_set.pop())
for i in range(test_size):
    test_set.add(entry_set.pop())
for i in range(valid_size):
    valid_set.add(entry_set.pop())

# 写入文件
with open(os.path.join(PATH, 'train.csv'), 'w', encoding='utf-8') as train_file:
    train_file.write('sentence,relation,head,head_offset,tail,tail_offset\n')
    while len(train_set) > 0:
        train_file.write(train_set.pop())
with open(os.path.join(PATH, 'test.csv'), 'w', encoding='utf-8') as test_file:
    test_file.write('sentence,relation,head,head_offset,tail,tail_offset\n')
    while len(test_set) > 0:
        test_file.write(test_set.pop())
with open(os.path.join(PATH, 'valid.csv'), 'w', encoding='utf-8') as valid_file:
    valid_file.write('sentence,relation,head,head_offset,tail,tail_offset\n')
    while len(valid_set) > 0:
        valid_file.write(valid_set.pop())
