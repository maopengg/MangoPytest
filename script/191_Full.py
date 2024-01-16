import json

import requests

url = "https://app-test.growknows.cn/dev-api/auth/oauth2/token"

payload = 'enterpriseName=yali008&userName=test005%40yali006.com&password=123456&code=AIgc2023aiGC&uuid=2abe6ff5e94249f58605a76b57c1adb9&mode=none&grant_type=password&account_type=admin&scope=server'
headers = {
  'Host': 'app-test.growknows.cn',
  'Connection': 'keep-alive',
  'Content-Length': '187',
  'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
  'Accept': 'application/json, text/plain, */*',
  'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
  'sec-ch-ua-mobile': '?0',
  'Authorization': 'Basic eHVleWk6eHVleWk=',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
  'sec-ch-ua-platform': '"Windows"',
  'Origin': 'https://app-test.growknows.cn',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://app-test.growknows.cn/',
  'Accept-Encoding': 'gzip, deflate, br',
  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
  'Cookie': 'SERVERCORSID=35bb5cb33daa9d99135c597101477544|1704248126|1704247959; SERVERID=35bb5cb33daa9d99135c597101477544|1704248126|1704247959'
}
# 设置代理
proxies = {
    "http": "http://127.0.0.1:8888",
    "https": "https://127.0.0.1:8888",
}

response = requests.request("POST", url, headers=headers, data=payload, proxies=proxies)
if response.status_code == 200:
    # Preprocess the response content to remove non-printable characters
    cleaned_content = response.content.decode('utf-8', errors='ignore').strip()

    # Try to parse the cleaned content as JSON
    try:
        data = json.loads(cleaned_content)
        print(data)
    except json.JSONDecodeError as e:
        print("JSON decoding error:", e)
else:
    print("Request failed with status code:", response.status_code)