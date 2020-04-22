# TODO:
# 1. 将cure全部转为推荐药物
# 2. 将分流后的结果全部分类存放好

# 根据NER标记筛选符合条件的关系
# 1）保留句子中出现两个或两个以上实体的句子
# 2）将句子前半后半分为两个短句，所有短句放在同一个大数组里。
# 例如，1治疗2，3造成4，5造成6，统一处理数组[1,2,3,4,5,6]，转码完成后，再两个两个地取出（1&2， 3&4）。
# 3）首先检查1和2的出现实体总数是否大于等于2，如果是，则根据1）保留到sentence_to_check
# 4）根据中间关键词，确定句子类别（使用relation filter的get_triple_category）
# 5）再检查1和2中是否分别出现了符合关键词要求的实体。如果出现了，选择1最右边的实体，和2最左边的实体，按照规定格式，存入result
# 6）对拼接起来的同一类的结果，最后要进行一次去重

# 最后，因为抽句子时，“相关疾病”和“相关症状”同为related，且多出了“可医治”cure，因此需要做最后处理
# 将related进行分流；将cure归类到推荐药物里

'''
rel == 治疗:   归为 可医治
治疗，head == 细菌，tail == 症状（如肉毒杆菌治疗肌肉痉挛）

rel == 推荐药物 就叫推荐药物
使用， head == 疾病，tail == 药物
（反过来）抑制，治疗，用于，预防 head== 药物，tail== 疾病，症状

rel == 引起: 就叫引起

引起，起的，head == 细菌/病因/病毒/疾病, tail == 症状/疾病/细菌（细菌引起细菌）
导致，所致head == 各种原因，tail == 疾病，症状
（反过来）由于，原因，head == 疾病，tail == 病因
可引，head == 疾病，tail == 症状，head == 原因，tail == 疾病
刺激，head == 病因，tail == 疾病/症状
感染，head == 细菌，病毒，tail == 疾病
因为，head == 疾病，tail == 病毒
产生，head == 病毒，tail == 症状
造成, 而出现

rel == 相似疾病，相似症状: 统一叫相关症状or相关疾病（需要判断head tail分类确定）

伴有，常有，典型，并发，继发，出现
 引起，导致，常伴有，表现为，并发症 是一种，最常见

 出现以上关键词，headtail同为疾病或症状

rel == 检测:

检查（可发现），head == 检查项目，tail == 疾病/症状
检测，head == 检查项目，tail == 病毒/药物（抗体类）
诊断，head == 检查项目，tail == 病毒

rel == 病症:

患者，head == 疾病，tail == 症状
主要，表现，不同程度，head == 疾病，tail == 症状
伴有，常有，典型，并发，继发，出现， head == 疾病，tail == 症状
临床表现
表现为，症状为，head== 疾病，tail==症状
（反过来）多见于，多发生，可见于，为特征 head== 症状，tail==疾病

Rel== 检查：
检查，检测 head==医学专科，tail==疾病

'''


import os
import re
import json

# 句子和对应的标记要放在同一个文件夹下，命名格式为"类别.txt", "类别_NER.json"
#PATH = r'd:\Project\Python\PythonGadgets\web_crawler\baike_spider-master\sentences\hudong'
PATH = r'F:\Projects\COVID19-kg\output_data\classless_relations\NER\data'
CATEGORY = 'recommend_drug'

# 找出单个半句中的所有实体
# 读入的参数：短句和对应的标记
# 返回list：[(entity1, type), (entity2, type), ...]
def find_entity(sentence_mark):
    entities = list() # [(entity1, type), (entity2, type), ...]
    current_entity = list() # [char1, char2, char3, ...]
    # current_word 当前正在读取的单字
    isReading = False
    # 当前是否正在读取
    for i in range(len(sentence_mark[0])):
        current_word = sentence_mark[0][i]
        if isReading is False and re.match('(B-)([A-Z]{1,3})', sentence_mark[1][i]) is not None:
            # 当前尚未在读，刚读到开头B，开始读取一个新实体
            isReading = True
            current_entity.append(current_word)
            current_type = sentence_mark[1][i]      # 保存当前实体的类别
        elif isReading is True and re.match('(B-)([A-Z]{3})', sentence_mark[1][i]) is not None:
            # 当前已经在读，又读到一个新的开头B，保存上一个实体并开始读取新实体
            current_entity = ''.join(current_entity)   # 拼接组成实体名字的单字
            entities.append((current_entity, current_type))

            current_entity = list()     # 清空current_entity准备读取新实体
            current_entity.append(current_word)
            current_type = sentence_mark[1][i]
        elif isReading is True and re.match('(I-)([A-Z]{3})', sentence_mark[1][i]) is not None:
            # 当前已经在读，读到和开头B相符的中间字I
            if sentence_mark[1][i][-1:-3] == current_type[-1:-3]:
                current_entity.append(current_word)
        elif isReading is True:
            # 当前已经在读，读到无关字符（O或者与开头B不同的I）
            isReading = False
            current_entity = ''.join(current_entity)  # 拼接组成实体名字的单字
            entities.append((current_entity, current_type))

            current_entity = list()  # 清空current_entity准备读取新实体
        elif isReading is False:
            # 当前已经尚未在读，且读到无关字符（O或者与开头B不同的I）
            pass

    return entities

# 判断句子是否符合要求
# 读入参数：句子前后半句及其对应标记（pair）；当前处理的category
def is_valid_relation(pair, category):
    # if category == 'cure':
    # # 治疗
    #     if 'B-BAC' in [sen_mark[1] for sen_mark in find_entity(pair[0])] \
    #     and {'B-SYM','B-DIS'} & set([sen_mark[1] for sen_mark in find_entity(pair[1])]) != set():
    #         return True
    # if category == 'recommend_drug':
    # # 推荐药物
    #     if 'B-DIS' in [sen_mark[1] for sen_mark in find_entity(pair[0])] \
    #     and 'B-DRU' in [sen_mark[1] for sen_mark in find_entity(pair[1])]:
    #         return True
    #     if 'B-DRU' in [sen_mark[1] for sen_mark in find_entity(pair[0])] \
    #     and 'B-DIS' in [sen_mark[1] for sen_mark in find_entity(pair[1])]:
    #         return True
    # if category == 'cause':
    # # 引起
    #     if {'B-BAC', 'B-DIS', 'B-VIR'} & set([sen_mark[1] for sen_mark in find_entity(pair[0])]) != set() \
    #     and {'B-DIS', 'B-SYM'} & set([sen_mark[1] for sen_mark in find_entity(pair[1])]) != set():
    #         return True
    # # TODO: 相似疾病症状
    # if category == 'detect':
    # # 检测
    #     if 'B-INS' in [sen_mark[1] for sen_mark in find_entity(pair[0])] \
    #     and {'B-DRU', 'B-DIS', 'B-SYM', 'B-VIR'} & set([sen_mark[1] for sen_mark in find_entity(pair[1])]) != set():
    #         return True
    # if category == 'disease':
    # # 病症
    #     if {'B-DIS', 'B-SYM'} & set([sen_mark[1] for sen_mark in find_entity(pair[0])]) != set() \
    #     and 'B-SYM' in [sen_mark[1] for sen_mark in find_entity(pair[1])]:
    #         return True
    # if category == 'inspection':
    # # 检查
    #     if 'B-SPE' in [sen_mark[1] for sen_mark in find_entity(pair[0])] \
    #     and {'B-DIS', 'B-SYM'} & set([sen_mark[1] for sen_mark in find_entity(pair[1])]) != set():
    #         return True

    if {'B-BAC', 'B-DIS', 'B-DRU', 'B-INS', 'B-SPE', 'B-SYM', 'B-VIR'} & set([sen_mark[1] for sen_mark in find_entity(pair[0])]) != set() \
    and {'B-BAC', 'B-DIS', 'B-DRU', 'B-INS', 'B-SPE', 'B-SYM', 'B-VIR'} & set([sen_mark[1] for sen_mark in find_entity(pair[1])]) != set():
        return True

# 从句子中抽出两个实体
# 返回两个值：关键词前后的实体(front, type), (back, type)
def pick_entity(pair):
    entities_in_front = find_entity(pair[0])
    entities_in_back = find_entity(pair[1])

    front_entity = entities_in_front[-1]
    back_entity = entities_in_back[0]
    return front_entity, back_entity

# 从B-INS, B-DIS等转换为实体类型单词
def get_type(tag):
    if tag == 'B-DIS':
        return 'disease'
    if tag == 'B-VIR':
        return 'virus'
    if tag == 'B-BAC':
        return 'bacteria'
    if tag == 'B-SYM':
        return 'symptom'
    if tag == 'B-INS':
        return 'inspection'
    if tag == 'B-DRU':
        return 'drug'
    if tag == 'B-SPE':
        return 'specialty'

# 从category转换为关系关键词
def get_verb(category, tag):
    # 可医治，推荐药物，引起，相似疾病症状，检测，病症，检查
    if category == 'cure':
        return '可医治'
    if category == 'recommend_drug':
        return '推荐药物'
    if category == 'cause':
        return '引起'
    if category == 'related_disease':
        return '相似疾病'
    if category == 'related_symptom':
        return '相似症状'
    if category == 'detect':
        return '检测'
    if category == 'disease':
        return '病症'
    if category == 'inspection' or category == 'inspect':
        return '检查'

# 导入实体名集合
def load_entity_names():
    disease = open(r'f:\Projects\corona\ngrams_baidu\entity_names\new_disease.txt', 'r', encoding='utf-8')
    drug = open(r'f:\Projects\corona\ngrams_baidu\entity_names\new_drug.txt', 'r', encoding='utf-8')
    bacteria = open(r'f:\Projects\corona\ngrams_baidu\entity_names\new_bacteria.txt', 'r', encoding='utf-8')
    virus = open(r'f:\Projects\corona\ngrams_baidu\entity_names\new_virus.txt', 'r', encoding='utf-8')
    symptom = open(r'f:\Projects\corona\ngrams_baidu\entity_names\new_symptom.txt', 'r', encoding='utf-8')
    inspect = open(r'f:\Projects\corona\ngrams_baidu\entity_names\new_inspection.txt', 'r', encoding='utf-8')
    specialty = open(r'f:\Projects\corona\ngrams_baidu\entity_names\new_specialty.txt', 'r', encoding='utf-8')

    # 载入别名文件，将别名放入实体名库中
    alias_bacteria = open(r'D:\Project\Python\PythonGadgets\web_crawler\baike_spider-master\alias/alias_bacteria.json', 'r', encoding='utf-8')
    alias_disease = open(r'D:\Project\Python\PythonGadgets\web_crawler\baike_spider-master\alias/alias_disease.json', 'r', encoding='utf-8')
    alias_drug = open(r'D:\Project\Python\PythonGadgets\web_crawler\baike_spider-master\alias/alias_drug.json', 'r', encoding='utf-8')
    alias_virus = open(r'D:\Project\Python\PythonGadgets\web_crawler\baike_spider-master\alias/alias_virus.json', 'r', encoding='utf-8')

    for line in disease:
        #print('正在载入：' + line.encode('gbk', 'ignore').decode('gbk'))
        disease_set.add(line.strip('\n'))
    for line in drug:
        #print('正在载入：' + line.encode('gbk', 'ignore').decode('gbk'))
        drug_set.add(line.strip('\n'))
    for line in bacteria:
        #print('正在载入：' + line.encode('gbk', 'ignore').decode('gbk'))
        bacteria_set.add(line.strip('\n'))
    for line in virus:
        #print('正在载入：' + line.encode('gbk', 'ignore').decode('gbk'))
        virus_set.add(line.strip('\n'))
    for line in symptom:
        #print('正在载入：' + line.encode('gbk', 'ignore').decode('gbk'))
        symptom_set.add(line.strip('\n'))
    for line in inspect:
        #print('正在载入：' + line.encode('gbk', 'ignore').decode('gbk'))
        inspect_set.add(line.strip('\n'))
    for line in specialty:
        #print('正在载入：' + line.encode('gbk', 'ignore').decode('gbk'))
        specialty_set.add(line.strip('\n'))

    # 载入别名
    alias_bacteria_json = json.load(alias_bacteria)
    for alias_list in alias_bacteria_json.values():
        for alias in alias_list:
            bacteria_set.add(alias)
    alias_disease_json = json.load(alias_disease)
    for alias_list in alias_disease_json.values():
        for alias in alias_list:
            disease_set.add(alias)
    alias_drug_json = json.load(alias_drug)
    for alias_list in alias_drug_json.values():
        for alias in alias_list:
            drug_set.add(alias)
    alias_virus_json = json.load(alias_virus)
    for alias_list in alias_virus_json.values():
        for alias in alias_list:
            virus_set.add(alias)

    # 删除错误的实体名或别名
    disease_set.remove('病')
    disease_set.remove('淋')
    disease_set.remove('疫')
    disease_set.remove('消')
    disease_set.remove('性疾病')
    disease_set.remove('痿')


    disease.close()
    drug.close()
    bacteria.close()
    virus.close()

# 根据实体名确认是否是正确关系
def are_valid_entities(category, front_entity, back_entity):
    if front_entity[0] == back_entity[0]:
    # 避免头尾相等
        return False

    if front_entity[0] in entity_name_set \
        and back_entity[0] in entity_name_set:
        return True


    # if category == 'cure':
    #     if front_entity[0] in bacteria_set \
    #     and back_entity[0] in (disease_set | symptom_set):
    #         return True
    # if category == 'recommend_drug':
    #     if front_entity[0] in (disease_set | symptom_set) \
    #     and back_entity[0] in drug_set:
    #         return True
    # if category == 'cause':
    #     if front_entity[0] in (bacteria_set | drug_set | disease_set) \
    #     and back_entity[0] in (symptom_set | disease_set):
    #         return True
    # if category == 'related':
    #     if front_entity[0] in disease_set and back_entity[0] in disease_set \
    #     or front_entity[0] in symptom_set and back_entity[0] in symptom_set:
    #         return True
    # if category == 'detect':
    #     if front_entity[0] in inspect_set \
    #     and back_entity[0] in (disease_set | symptom_set | virus_set | bacteria_set | drug_set):
    #         return True
    # if category == 'disease':
    #     if front_entity[0] in disease_set and back_entity[0] in symptom_set \
    #     or front_entity[0] in symptom_set and back_entity[0] in disease_set:
    #         return True
    # if category == 'inspect':
    #     if front_entity[0] in specialty_set \
    #     and back_entity[0] in (disease_set | symptom_set | virus_set | bacteria_set):
    #         return True

    return False

# 对输出结果的最后处理
# 1）将cure转为推荐药物（重命名关系）
# 2) 分流相关疾病and相关症状
# 3) 对“引起”中的“疾病引起疾病”归类到“相关疾病”；“疾病引起症状”归类到“病症”
# 4）对部分特殊三元组的头尾进行交换，使其符合逻辑
def post_process(category, front_entity, back_entity):
    new_category = category
    new_front = front_entity
    new_back = back_entity

    if category == 'cure':
    # 将“可医治”归类到“推荐药物”
        category = 'recommend_drug'
    if category == 'related':
    # 将“相似疾病”和“相似症状”分流
        if front_entity[0] in disease_set:
            new_category = 'related_disease'
        else:
            new_category = 'related_symptom'
    if category == 'cause':
    # 将“引起”中的“疾病引起疾病”归类到“相关疾病”；“疾病引起症状”归类到“病症”
        if front_entity[0] in disease_set and back_entity[0] in disease_set:
            new_category = 'related_disease'
        if front_entity[0] in disease_set and back_entity[0] in symptom_set:
            new_category = 'disease'

    # 对部分三元组的头尾进行交换，使其符合逻辑
    if new_category == 'recommend_drug':
        if front_entity[0] in drug_set and back_entity[0] in (disease_set | symptom_set):
            new_back = front_entity
            new_front = back_entity
    if new_category == 'disease':
        if front_entity[0] in symptom_set and back_entity[0] in disease_set:
            new_back = front_entity
            new_front = back_entity

    return new_category, new_front, new_back

# 载入原始句子文档和对应的标记文档
sentence_file = open(os.path.join(PATH, CATEGORY + '.txt'), 'r', encoding='utf-8')
mark_file = open(os.path.join(PATH, CATEGORY + '_NER.json'), 'r', encoding='utf-8')

# 读取文件内容，构成[[(1-A, mark)，(1-B, mark)],[(2-A, mark), (2-B, mark)], ...]
# 这里需要注意一点：做标记的时候是进行了空格筛选的，这里要保持筛选规则一致，才能让句子对的上
sentence_and_mark = list()  # 保存从文件中读取的句子和对应的标记

# 读取标记文档
mark = json.loads(mark_file.readline())

# 读取句子文档，构成句子-标记的映射
# 处理标记和实际文本长度不匹配的情况
i = 0
for line in sentence_file:
    fragments = line.split(';;;;ll;;;;')

    if len(fragments) == 3 and re.match('[ \u2003]+', fragments[0]) is None and re.match('[ \u2003]+',  fragments[2]) is None:
        # 构成[[(1-A, mark)，(1-B, mark)],[(2-A, mark), (2-B, mark)], ...]

        # 处理标记和实际文本长度不匹配的情况，对长的部分进行截断
        if len(fragments[0]) > len(mark[i][0]):
        # 前半句文本>前半句标记
            fragments[0] = fragments[0][0:len(mark[i][0])]
        if len(fragments[0]) < len(mark[i][0]):
        # 前半句文本<前半句标记
            mark[i][0] = mark[i][0][0:len(fragments[0])]
        if len(fragments[2]) > len(mark[i][1]):
        # 后半句文本>后半句标记
            fragments[2] = fragments[2][0:len(mark[i][1])]
        if len(fragments[2]) < len(mark[i][1]):
        # 后半句文本<后半句标记
            mark[i][1] = mark[i][1][0:len(fragments[2])]

        sentence_and_mark.append([(fragments[0], mark[i][0]), (fragments[2], mark[i][1])])
        if i + 1 < len(mark):
            i += 1

# 找出标记文本中的实体，对出现实体数>=2的句子，保留到sentence_to_check备查
# 判断前后半句是否出现了符合类别要求的实体，符合者保留到valid_relations
sentence_to_check = list()  # 备查的句子
relations = list()          # 类别符合规范的关系，但还需要经过实体库检测
for pair in sentence_and_mark:
    if len(find_entity(pair[0])) + len(find_entity(pair[1])) > 1:
        sentence_to_check.append(pair[0][0] + ' ' + CATEGORY + ' ' + pair[1][0])
        if is_valid_relation(pair, CATEGORY) is True:
            relations.append(pair)
            print('初步筛选：实体类别符合的关系：' + CATEGORY + repr(pair).encode('gbk', 'ignore').decode('gbk'))
        else:
            print('初步筛选：丢弃实体类别不符关系：' + CATEGORY + repr(pair).encode('gbk', 'ignore').decode('gbk'))


# 输出结果：1）备查句合集
if not os.path.exists(os.path.join(PATH, 'to_check')):
    os.mkdir(os.path.join(PATH, 'to_check'))
sentence_to_check_file = open(os.path.join(PATH, 'to_check', CATEGORY + '_to_check.txt'), 'w', encoding='utf-8')

for sentence in sentence_to_check:
    sentence_to_check_file.write(sentence)
    if sentence[-1] != '\n':
        sentence_to_check_file.write('\n')
sentence_to_check_file.close()

# 输出结果：2）初步筛选并格式化后的关系合集
if not os.path.exists(os.path.join(PATH, 'relations')):
    os.mkdir(os.path.join(PATH, 'relations'))
relations_file = open(os.path.join(PATH, 'relations', CATEGORY + '_relation_to_check.txt'), 'w', encoding='utf-8')

for pair in relations:
    # 找出选入三元组的实体
    front_entity, back_entity = pick_entity(pair)
    # 写head和tail的所属类别
    relations_file.write(get_type(front_entity[1]) + ';;;;ll;;;;' + get_type(back_entity[1]) + ':')
    # 写三元组
    try:
        relations_file.write(front_entity[0] + ';;;;ll;;;;' + get_verb(CATEGORY, front_entity[1]) + ';;;;ll;;;;' + back_entity[0] + '\n')
    except:
        print('1. error: ' + front_entity[0] + ' ' + front_entity[1])
relations_file.close()

# 输出结果：3）经过实体库筛选后的关系合集
disease_set = set()
drug_set = set()
bacteria_set = set()
virus_set = set()
symptom_set = set()
inspect_set = set()
specialty_set = set()
sets = [disease_set, drug_set, bacteria_set, virus_set, symptom_set, inspect_set, specialty_set]
# 导入实体名集合
load_entity_names()

# 0412 导入整体实体名集合
entity_name_set = set()
with open(r'F:\Projects\COVID19-kg\entity_classless_relation_extractor\total_entity.txt', 'r', encoding='utf-8') as entity_name_file:
    for line in entity_name_file:
        entity_name_set.add(line.strip('\n'))
# 删除错误的实体名或别名
    entity_name_set.remove('病')
    entity_name_set.remove('淋')
    entity_name_set.remove('疫')
    entity_name_set.remove('消')
    entity_name_set.remove('性疾病')
    entity_name_set.remove('痿')
print('实体名集合载入完成。')

# 判断关系中的实体名是否在实体库中
# 若合法，则对关系作最后处理，并保存结果
valid_relations_file = open(os.path.join(PATH, 'relations', CATEGORY + '_relation_final.txt'), 'w', encoding='utf-8')
valid_relations_set = set()     # 用于去重
for pair in relations:
    # 找出选入三元组的实体
    front_entity, back_entity = pick_entity(pair)
    # 判断关系中的实体名是否在实体库中
    if are_valid_entities(CATEGORY, front_entity, back_entity):
        # 对关系作最后处理
        current_category, front_entity, back_entity = post_process(CATEGORY, front_entity, back_entity)
        # 保存最终结果
        # 查重
        current_pair = (front_entity, back_entity)
        if current_pair in valid_relations_set:
            continue
        else:
            valid_relations_set.add(current_pair)
            print('最终入选：' + repr(pair).encode('gbk', 'ignore').decode('gbk'))
        # 写head和tail的所属类别
        #valid_relations_file.write(get_type(front_entity[1]) + ';;;;ll;;;;' + get_type(back_entity[1]) + ':')
        # 写三元组
        try:
            valid_relations_file.write(front_entity[0] + ';;;;ll;;;;' + get_verb(current_category, front_entity[1]) + ';;;;ll;;;;' + back_entity[0] + '\n')
        except:
            print('2. error: ' + front_entity[0] + ' ' + front_entity[1])
    else:
        print(('关系中出现的实体不在实体库中：' + front_entity[0] + CATEGORY + back_entity[0]).encode('gbk', 'ignore').decode('gbk'))
valid_relations_file.close()

# 关闭数据源
sentence_file.close()
mark_file.close()


