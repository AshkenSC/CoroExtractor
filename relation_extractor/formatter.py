# 对抽出的句子按照模型要求进行格式化
# 将自动读取SOURCE文件夹下所有的JSON

import json
import os

SOURCE = r'f:\Projects\COVID19-kg\output_data\sentences\unformatted'
DEST = r'f:\Projects\COVID19-kg\output_data\sentences\formatted\formatted_sentences.json'


def load_sentences(source):
    total_sentences = list()
    for root, dirs, files in os.walk(source):
        for file in files:
            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                sub_sentences = json.loads(f.read())
                total_sentences += sub_sentences
    return total_sentences


# 载入实体名和类型的对应字典
def load_entity_type_dict():
    # 类型名中英文对照
    entity_cn_en = {
        'bacteria': '细菌',
        'disease': '疾病',
        'symptom': '症状',
        'department': '科室',
        'item': '项目',
        'drug': '药物',
        'virus': '病毒',
    }

    entity_type = dict()
    for root, dirs, files in os.walk(r'f:\Projects\COVID19-kg\source_data\entity_names\entity_names_v6\dataset\entity'):
        for file in files:
            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entity_type[line.strip('\n')] = entity_cn_en[file.replace('_entity.txt', '')]
                    except:
                        print('error')
                        print(line.encode('gbk', 'ignore').decode('gbk'))

    return entity_type


def locate_entity(entry):
    sentence = entry['sentence']
    head = entry['head']
    tail = entry['tail']
    head_start = sentence.find(head)
    head_end = head_start + len(head)
    tail_start = sentence.find(head)
    tail_end = tail_start + len(tail)
    return head_start, head_end, tail_start, tail_end


def parse(sentence):
    tokens = list()
    for char in sentence:
        tokens.append(char)
    return tokens


def processor(sentences_and_entities, entity_type):
    # tokens, entities, relations, orig_id
    result = list()

    entity_id = 0
    for entry in sentences_and_entities:
        new_entry = dict()
        # 对head和tail在句子中的位置进行定位
        head_start, head_end, tail_start, tail_end = locate_entity(entry)

        # 添加tokens字段。对句子进行分字
        new_entry['tokens'] = parse(entry['sentence'])

        # 添加entities字段。只要head和tail有一个没找到，则二者都不添加
        new_entry['entities'] = []
        if entry['tail'] == '血栓性血小板减少性紫癜':
            print('1')
        if head_start != -1 and tail_start != -1:
            head_dict = {
                'type': entity_type[entry['head']],
                'start': head_start,
                'end': head_end
            }
            tail_dict = {
                'type': entity_type[entry['tail']],
                'start': tail_start,
                'end': tail_end
            }
            new_entry['entities'].append(head_dict)
            new_entry['entities'].append(tail_dict)

        # 添加relations字段。该字段留空
        new_entry['relations'] = []

        # 添加orig_id字段
        new_entry['orig_id'] = entity_id
        entity_id += 1

        # 将新条目添加到结果list中
        if len(new_entry['tokens']) <= 150:
            result.append(new_entry)
        print(entity_id)

    return result


if __name__ == '__main__':
    # 载入并整合句子源文件
    sentences_and_entities = load_sentences(SOURCE)
    # 载入实体名和类型的对应字典
    entity_type = load_entity_type_dict()
    # 给每条数据标号
    # 进行句子的分字
    # 标注实体的类型和在句子中的起止位置（type, start, end）
    result = processor(sentences_and_entities, entity_type)
    # 将处理完成的数据写入JSON文件
    print ('正在写入……')
    with open(DEST, 'w', encoding='utf-8') as output_file:
        output_file.write(json.dumps(result, ensure_ascii=False, indent=4))
    print('写入完成')
