# -*- coding: utf-8 -*-
import os, requests, uuid, json

# key_var_name = 'TRANSLATOR_TEXT_SUBSCRIPTION_KEY'
# if not key_var_name in os.environ:
#     raise Exception('Please set/export the environment variable: {}'.format(key_var_name))
# subscription_key = os.environ[key_var_name]
subscription_key = '010017e874f944a896bab58beb171d32'

# endpoint_var_name = 'TRANSLATOR_TEXT_ENDPOINT'
# if not endpoint_var_name in os.environ:
#     raise Exception('Please set/export the environment variable: {}'.format(endpoint_var_name))
# endpoint = os.environ[endpoint_var_name]
endpoint = 'https://covid19-kg.cognitiveservices.azure.com'

path = '/translate?api-version=3.0'
params = '&to=de'
#constructed_url = endpoint + path + params
constructed_url = 'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to=de'

headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}

body = [{
    'text': 'Hello World!'
}]

request = requests.post(constructed_url, headers=headers, json=body)
response = request.json()

print(json.dumps(response, sort_keys=True, indent=4,
                 ensure_ascii=False, separators=(',', ': ')))