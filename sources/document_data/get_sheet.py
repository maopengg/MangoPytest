# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-04-01 21:12
# @Author : 毛鹏

import requests

url = "https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/ZQfZsC7IShpkGytZLoKc1gbXnPS/sheets/query"
payload = ''

headers = {
    'Authorization': 'Bearer u-eWySs_.SNe2bH5mYLyMuEPl00ZCN4071qq0011K085s1'
}

response = requests.request("GET", url, headers=headers, data=payload)
print(response.text)
