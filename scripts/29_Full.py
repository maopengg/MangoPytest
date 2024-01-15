import json

import requests

url = "https://app-test.growknows.cn/dev-api/auth/oauth2/token"

payload = 'enterpriseName=yali008&userName=test005%40yali006.com&password=123456&code=AIgc2023aiGC&uuid=2abe6ff5e94249f58605a76b57c1adb9&mode=none&grant_type=password&account_type=admin&scope=server'
headers = {
  'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
  'Authorization': 'Basic eHVleWk6eHVleWk=',
  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
}

response = requests.request("POST", url, headers=headers, data=payload)
print(json.dumps(headers))
print(response.text)
