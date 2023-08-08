# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-07 17:27
# @Author : 毛鹏
import requests
from tools.testdata.memory_cache import CacheData

url = CacheData.get(
    'host') + '/backend/api-auth/oauth/token?username=admin&password=21232f297a57a5a743894a0e4a801fc3&grant_type=password_code'
headers = {
    'Authorization': 'Basic d2ViQXBwOndlYkFwcA==',
    'Accept': 'application/json, text/plain, */*',
}
r = requests.post(url=url, headers=headers)
CacheData.set('token', r.json().get("data").get('access_token'))
