# 根据head和tail的属性，以及关系relationship的关键字，将获取到的关系进行筛选
# 修改词条名集合load_entity_names，修改DATA_SOURCE，修改OUTPUT
# 注意检查不同数据源的不同格式，修改parse_line函数
DATA_SOURCE = r'D:\Project\Python\PythonGadgets\web_crawler\baike_spider-master\ngrams_addline\3_alias2\virus\detail\3_detail.txt'
OUTPUT = r'F:\Projects\COVID19-kg\output_data\classless_relations\link\raw_triples\raw_triples_virus.txt'

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

'''
以rel治疗为例
1，遍历细菌、病毒、疾病里所有的3_detail文件行，查看其中的calculate行。只要三个字里包含治疗相关的关键字（治疗，抑制，用于等），就把该calculate下的所有三元组收录待筛查；
2，符合条件的三元组为：head和tail都属于某几种特定的类，如head必须是 药物，手术，治疗 tail是疾病，细菌，病毒等
3，最后将结果存为以下格式：
head类别;;;;ll;;;;tail类别:head;;;;ll;;;;rel;;;;ll;;;;tail
'''
import re
import json

# 检查calculate行，根据其找到的关键字属于哪个类别i，将其下的三元组分到那个类别i
def find_keyword(line, word_list):
    for word in word_list:
        if word in line:
            return True
    return False

# 读取三元组
def parse_line(line):
    # 三元组格式1
    # head = re.search(r'(head:)([\u4e00-\u9fa5]*)', line).group(2)
    # tail = re.search(r'(tail)([\u4e00-\u9fa5]*)', line).group(2)
    # rel = re.search(r'(rel:)([\u4e00-\u9fa5]*)', line).group(2)
    # triple = [head, tail, rel]

    # 三元组格式2
    triple = line.split(';;;;ll;;;;')
    return triple

# 判断三元组是否合法
def is_valid(triple, category):
    # 检查head tail类别是否合法
    if triple[0] == triple[1] or triple[0] is None or triple[1] is None or triple[0] == '' or triple[1] == '':
        return False
    if triple[0] in entity_name_set and triple[1] in entity_name_set:
        return True
    return False

    # if triple[0] == triple[1]:
    #     return False
    # if category == 0:
    # # rel治疗， 要求head属于药物，手术，细菌，tail属于疾病或症状
    #     if (triple[0] in drug_set or triple[0] in bacteria_set) and\
    #         (triple[1] in symptom_set or triple[1] in disease_set):
    #         return True
    # elif category == 1:
    # # rel推荐药物，要求head属于疾病，tail属于药物
    #     if triple[0] in disease_set and triple[1] in drug_set:
    #         return True
    # elif category == 2:
    # # rel引起，要求head属于细菌，病毒，疾病，tail属于症状，疾病
    #     if (triple[0] in bacteria_set or triple[0] in virus_set or triple[0] in disease_set) and\
    #             (triple[1] in symptom_set or triple[1] in disease_set):
    #         return True
    # elif category == 3:
    # # rel相似疾病，要求head和tail同时属于疾病，或head和tail同时属于症状
    #     if (triple[0] in disease_set and triple[1] in disease_set) or\
    #             (triple[0] in symptom_set and triple[1] in symptom_set):
    #         return True
    # elif category == 4:
    # # rel检测，要求head为检查项目，tail为疾病，症状，病毒，细菌，药物
    #     if triple[0] in inspect_set and triple[1] in (disease_set|symptom_set|virus_set|bacteria_set|drug_set):
    #         return True
    # elif category == 5:
    # # rel病症，要求head为疾病，tail为症状；或head为症状，tail为疾病
    #     if (triple[0] in disease_set and triple[1] in symptom_set) or (triple[0] in symptom_set and triple[1] in disease_set):
    #         return True
    # elif category == 6:
    # # rel检查，要求head为医学专科，tail为疾病，症状，病毒，细菌
    #     if triple[0] in specialty_set and triple[1] in (disease_set|symptom_set|virus_set|bacteria_set):
    #         return True


# 根据类别不同，重命名三元组的rel部分
# 对部分特殊三元组的头尾进行交换，使其符合逻辑
# 0-治疗，1-推荐药物，2-引起，3-相关疾病or相关症状，4-检测，5-病症，6-检查
def rename_triple(triple, category):
    if category == 0:
        triple[2] = '可医治'
    elif category == 1:
        # 翻转头尾：抑制，治疗，用于，预防
        if re.search('(抑制)|(治疗)|(用于)|(预防)', triple[2]) is not None:
            temp = triple[1]
            triple[1] = triple[0]
            triple[0] = temp
        triple[2] = '推荐药物'
    elif category == 2:
        # 翻转头尾：由于，原因
        if re.search('由于|原因', triple[2]) is not None:
            temp = triple[1]
            triple[1] = triple[0]
            triple[0] = temp
        triple[2] = '引起'
    elif category == 3:
        if triple[0] in disease_set:
            triple[2] = '相关疾病'
        else:
            triple[2] = '相关症状'
    elif category == 4:
        triple[2] = '检测'
    elif category == 5:
        # 翻转头尾：多见于，多发生，可见于，为特征
        if re.search('多见于|多发生|可见于|为特征', triple[2]) is not None:
            temp = triple[1]
            triple[1] = triple[0]
            triple[0] = temp
        triple[2] = '病症'
    elif category == 6:
        triple[3] = '检查'
    return triple

# 获取实体类别，返回类别名字符串
def get_triple_category(name):
    category_name = ['disease', 'drug', 'bacteria', 'virus', 'symptom', 'inspect', 'specialty']
    for i in range(len(sets)):
        if name in sets[i]:
            return category_name[i]

# 导入词条名集合
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
        print('正在载入：' + line.encode('gbk', 'ignore').decode('gbk'))
        disease_set.add(line.strip('\n'))
    for line in drug:
        print('正在载入：' + line.encode('gbk', 'ignore').decode('gbk'))
        drug_set.add(line.strip('\n'))
    for line in bacteria:
        print('正在载入：' + line.encode('gbk', 'ignore').decode('gbk'))
        bacteria_set.add(line.strip('\n'))
    for line in virus:
        print('正在载入：' + line.encode('gbk', 'ignore').decode('gbk'))
        virus_set.add(line.strip('\n'))
    for line in symptom:
        print('正在载入：' + line.encode('gbk', 'ignore').decode('gbk'))
        symptom_set.add(line.strip('\n'))
    for line in inspect:
        print('正在载入：' + line.encode('gbk', 'ignore').decode('gbk'))
        inspect_set.add(line.strip('\n'))
    for line in specialty:
        print('正在载入：' + line.encode('gbk', 'ignore').decode('gbk'))
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

    disease.close()
    drug.close()
    bacteria.close()
    virus.close()

disease_set = set()
drug_set = set()
bacteria_set = set()
virus_set = set()
symptom_set = set()
inspect_set = set()
specialty_set = set()
sets = [disease_set, drug_set, bacteria_set, virus_set, symptom_set, inspect_set, specialty_set]

# 0412 载入整体实体集合名
entity_name_set = set()
with open(r'F:\Projects\COVID19-kg\entity_classless_relation_extractor\total_entity.txt', 'r', encoding='utf-8') as entity_name_file:
    for line in entity_name_file:
        entity_name_set.add(line.strip('\n'))
print('实体名集合载入完成。')


# 设置过滤关键字数组
# 0-治疗，1-推荐药物，2-引起，3-相关疾病or相关症状，4-检测，5-病症，6-检查
keywords = [['可医治', ('治疗')],
            ['推荐药物', ('使用', '抑制', '治疗', '用于', '预防')],
            ['引起', ('引起', '导致', '所致', '由于', '原因', '刺激', '感染', '因为', '产生', '造成', '而出现', '是一种', '最常见')],
            ['相关疾病', '相关症状', ('伴有', '常有', '典型', '并发', '继发', '出现', '引起', '导致', '常伴有', '表现为', '并发症')],
            ['检测', ('检查', '可发现', '检测', '诊断')],
            ['病症', ('患者', '主要', '表现', '不同程度', '伴有', '常有', '典型', '并发', '继发', '出现', '临床表现', '表现为', '症状为', '多见于', '多发生', '可见于', '为特征')],
            ['检查', ('检查', '检测')],
            ]

# 导入词条名集合
load_entity_names()

# 导入文件，对calculate行判断其类别；对三元组行获取其内容。
data_source = open(DATA_SOURCE, 'r', encoding='utf-8')
valid_triples = list()          # 用于存储合法的待输出triple
for i in range(7):
    valid_triples.append(list())

# 检查三元组是否符合i类的各种条件，head，tail是否符合规定类别。如果符合类别，则重命名rel后输出
# 对相似疾病or相似症状，必须根据head和tail的类别进行判断是哪个，再做重命名
isReadingTriple = False
for line in data_source:
    if 'calculate' in line:
        for i in range(len(keywords)):
            # 首先看calculate后的词条是否包含关键字
            if find_keyword(line, keywords[i][-1]):
                # 若包含，则预设其属下三元组的分类
                print(line.encode('GBK','ignore').decode('GBk'))
                current_category = i
                isReadingTriple = True
                break
            else:
                isReadingTriple = False
    elif isReadingTriple is True:
        new_triple = parse_line(line)
        # TODO: 检查head tail类别是否合法（为研究原因暂时不检查类别是否正确）
        if is_valid(new_triple, current_category):
            new_triple = rename_triple(new_triple, current_category)
            valid_triples[current_category].append(new_triple)
            print('发现有效三元组：', end='')
            print(repr(new_triple).encode('GBK','ignore').decode('GBk'))
        else:
            print('无效：' + repr(new_triple).encode('gbk', 'ignore').decode('gbk'))
data_source.close()

# 结果写入文件
# 用函数get_triple_category输出head和tail属于哪个类别
# 对输出的triple存入dedup_triple_list用于进行去重
output = open(OUTPUT, 'w', encoding='utf-8')
dedup_triple_list = set()
for sublist in valid_triples:
    for triple in sublist:
        if tuple(triple) not in dedup_triple_list:
            # 将当前三元组存入去重列表里
            dedup_triple_list.add(tuple(triple))
            # 显示结果
            print('正在保存：' + repr(triple).encode('GBK','ignore').decode('GBk'))
            # 输出head和tail的类别
            #output.write(get_triple_category(triple[0]) + ';;;;ll;;;;' + get_triple_category(triple[1]) + ':')
            # 输出三元组
            output.write(triple[0] + ';;;;ll;;;;' + triple[2] + ';;;;ll;;;;' + triple[1] + '\n')
output.close()