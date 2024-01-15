#!/usr/bin/python高级
# -*- coding: UTF-8 -*-
import time

import requests

url = "https://app-dev.growknows.cn/dev-api/auth/oauth2/token"
headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "Authorization": "Basic eHVleWk6eHVleWk="
}

test_case = {
    "enterpriseName": "administrator",
    "userName": "admin",
    "password": "admin123",
    "code": "AIgc2023aiGC",
    "uuid": "21cfcf8feaf84ed4a831c80662227d8c",
    "mode": "none",
    "grant_type": "password",
    "account_type": "admin",
    "scope": "server"
}
html = requests.post(url, headers=headers, data=test_case)
headers["Authorization"] = html.json()["data"]["access_token"]
url2 = f"https://app-dev.growknows.cn/dev-api/business/knowledge-doc/list?field=createTime&order=descend&page=1&pageSize=500&id=1731514339454676994"
html = requests.get(url2, headers=headers)
for i in html.json()["data"]["records"]:
    if i["type"] == "pdf" and i["status"] == "1":
        url3 = f"https://app-dev.growknows.cn/dev-api/business/knowledge-doc/retry?id={i["id"]}"
        html = requests.get(url3, headers=headers)
        print(i["name"])
        time.sleep(1)
