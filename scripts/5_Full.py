#!/usr/bin/python高级
# -*- coding: UTF-8 -*-
import requests

url = 'https://www.jianguoyun.com/d/login'
headers = {'Host': 'www.jianguoyun.com', 'Connection': 'keep-alive', 'Content-Length': '188', 'Cache-Control': 'max-age=0', 'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'Upgrade-Insecure-Requests': '1', 'Origin': 'https://www.jianguoyun.com', 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7', 'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-User': '?1', 'Sec-Fetch-Dest': 'document', 'Referer': 'https://www.jianguoyun.com/d/signup', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'}
cookies = {'referrer': 'https://www.jianguoyun.com/', 'page_locale': 'zh'}
test_case = {'login_email': '729164035%40qq.com', 'login_password': 'm729164035', 'login_dest_uri': '%2Fd%2Fhome', 'custom_ticket': 'ET_P5Js-RpyvINmdGCcZMg', 'exp': '1706864710165', 'sig': 'zULwNawd07ro7isZTIDbl7TMK0I%3D', 'reusable': 'false'}

html = requests.post(url, headers=headers, verify=False, cookies=cookies, json=test_case)
print(len(html.text))
print(html.text)
