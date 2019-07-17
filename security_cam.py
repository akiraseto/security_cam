import requests
import sys
import config
import urllib.parse as parse

# LINE Notifyトークン - 以下を書き換えて利用します★
TOKEN = config.TOKEN
API = 'https://notify-api.line.me/api/notify'

# LINE Notifyにデータをポスト
post_data = {'message': sys.argv[1]}
headers = {'Authorization': 'Bearer ' + TOKEN}
res = requests.post(API, data=post_data,
                headers=headers)
print(res.text) # 結果を表示




