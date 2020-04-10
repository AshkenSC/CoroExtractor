import json, os

files = os.listdir('./data')[:-1]
with open('baike.json', 'wb') as fp:
    for file in files:
        if file.endswith('.json'):
            with open(os.path.join('data', file), 'rb') as f:
                fp.write(f.read())