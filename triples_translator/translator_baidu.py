# 调用百度API进行翻译
# https://www.cnblogs.com/wdee/p/9878658.html

import hashlib
import json
import random
import time
import requests
import re
import winsound

SOURCE = r'f:\Projects\COVID19-kg\source_data\dataset0501\Chinese\text_property\zhwiki_text_triples.txt'
DEST = r'f:\Projects\COVID19-kg\source_data\dataset0501\English\text_property\zhwiki_text_triples.txt'
BATCH_SIZE = 30

url = "http://api.fanyi.baidu.com/api/trans/vip/translate"
app_id = '20200517000458913'  # 你的appid
secretKey = '4mfE3hLAEAygwTFSQz3l'  # 你的密钥
salt = random.randint(32768, 65536)


def get_tra_res(q, from_lang='zh', to_lang='en'):
    # 生成签名
    sign = app_id + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    # post请求参数
    data = {
        "appid": app_id,
        "q": q,
        "from": from_lang,
        "to" : to_lang,
        "salt" : str(salt),
        "sign" : sign,
    }
    # post请求
    time.sleep(3)
    res = requests.post(url, data=data)
    # 返回一个json, 得到若干行翻译结果，进行拼接整理
    trans_result = ''
    for line in json.loads(res.content).get('trans_result'):
        trans_result += line.get("dst") + '\n'
    return trans_result


# 读取txt文件
with open(SOURCE, 'r', encoding='utf-8') as source_file:
    print('源文件打开成功，当前正在翻译: ' + SOURCE)
    # 打开写入文件，分批翻译并写入
    with open(DEST, 'a+', encoding='utf-8') as dest_file:
        lines = source_file.readlines()
        end_line = lines[-1]
        output = ''
        i = 0
        while i < len(lines):
            sub_input = ''
            print('翻译第' + str(i) + '到', end='')
            # 拼接字符串
            for j in range(BATCH_SIZE):
                # lines[i] = lines[i].replace('\n', r'\n')
                sub_input += lines[i]
                i += 1
                if i == len(lines) or j == BATCH_SIZE - 1:
                    print(str(i) + '行')
                    break
            # 翻译拼接好的字符串
            while True:
                try:
                    translated = get_tra_res(sub_input)
                    translated = re.sub(r'([ ;]+)ll([ ;]+)', ';;;;ll;;;;', translated)
                    dest_file.write(translated)
                except:
                    print('error: ' + str(i))
                    time.sleep(5)
                    continue
                break
print('翻译完成。')
winsound.Beep(500, 500)
winsound.Beep(600, 500)
winsound.Beep(800, 700)

