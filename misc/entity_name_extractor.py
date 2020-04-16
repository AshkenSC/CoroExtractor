# 从文件中提取出仅含有实体名的名单txt

'''
# V1
# 整理实体名称并分类存储
disease_set = set()
drug_set = set()
inspection_set = set()
specialty_set = set()
virus_set = set()
symptom_set = set()

# 读取
source_file = open('../source_data/entity_names/cdd_system_entity_type.txt', 'r', encoding='utf-8')
for line in source_file:
    line_list = line.split(';;;;ll;;;;')
    if line_list[2].strip('\n') == '疾病':
        disease_set.add(line_list[0])
    elif line_list[2].strip('\n') == '药品':
        drug_set.add(line_list[0])
    elif line_list[2].strip('\n') == '检查科目':
        inspection_set.add(line_list[0])
    elif line_list[2].strip('\n') == '症状':
        symptom_set.add(line_list[0])
source_file.close()

source_file2 = open('F:\Projects\COVID19-kg\source_data\entity_names\disease_baike_entity_type.txt', 'r', encoding='utf-8')
for line in source_file2:
    line_list = line.split(';;;;ll;;;;')
    if line_list[2].strip('\n') == '疾病':
        disease_set.add(line_list[0])
    elif line_list[2].strip('\n') == '药品':
        drug_set.add(line_list[0])
    elif line_list[2].strip('\n') == '检查科目':
        inspection_set.add(line_list[0])
    elif line_list[2].strip('\n') == '症状':
        symptom_set.add(line_list[0])
source_file2.close()


# 写入
disease_file = open('../output_data/entity_names/disease.txt', 'a', encoding='utf-8')
drug_file = open('../output_data/entity_names/drug.txt', 'a', encoding='utf-8')
inspection_file = open('../output_data/entity_names/inspection.txt', 'a', encoding='utf-8')
symptom_file = open('../output_data/entity_names/symptom.txt', 'a', encoding='utf-8')

for item in disease_set:
    disease_file.write(item + '\n')
    print(item.encode('GBK', 'ignore').decode('GBk'))
for item in drug_set:
    drug_file.write(item + '\n')
    print(item.encode('GBK', 'ignore').decode('GBk'))
for item in inspection_set:
    inspection_file.write(item + '\n')
    print(item.encode('GBK', 'ignore').decode('GBk'))
for item in symptom_set:
    symptom_file.write(item + '\n')
    print(item.encode('GBK', 'ignore').decode('GBk'))

disease_file.close()
drug_file.close()
inspection_file.close()
symptom_file.close()


'''


'''
# V2

'''
'''
SOURCE = r'../source_data/entity_names/entity_names_v0405/original/virus_entity_type.txt'
DEST = r'F:\Projects\COVID19-kg\source_data\entity_names\entity_names_v0405\virus.txt'

source_file = open(SOURCE, 'r', encoding='utf-8')
with open(DEST, 'a', encoding='utf-8') as output_file:
    name_set = set()

    with open(DEST, 'r', encoding='utf-8') as f:
        name_set.add(f.readline().strip('\n'))

    for line in source_file:
        name_set.add(line.split(';;;;ll;;;;')[0])
    for item in name_set:
        output_file.write(item + '\n')
        print(item.encode('GBK', 'ignore').decode('GBk'))
source_file.close()
'''

# V3 因为要求实体名单不是从line['name']取，而是直接取原来名单里的实体名，所以必须通过
# “判断这个URL是否有效，如果有效就记录当前的原实体名”来记录
r'''
import json
json_file =  open(r'F:\Projects\COVID19-kg\source_data\baidu_json\v3\virus.json', 'r', encoding='utf-8')
name_list = list()
for json_line in json_file:
    line = json.loads(json_line)
    name_list.append(line['name'])
    name_list = sorted(name_list)

with open(r'F:\Projects\COVID19-kg\output_data\entity_names\v0410\virus.txt', 'w', encoding='utf-8') as output:
    for name in name_list:
        output.write(name + '\n')
json_file.close()

txt_file = open(r'C:\Users\ASUS\Desktop\virus.txt', 'r', encoding='utf-8')
with open(r'C:\Users\ASUS\Desktop\virus2.txt', 'w', encoding='utf-8') as txt_out:
    name_list = list()
    for line in txt_file:
        name_list.append(line.strip('\n'))
    name_list = sorted(name_list)
    for name in name_list:
        txt_out.write(name + '\n')
txt_file.close()
'''




