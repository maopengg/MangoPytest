#!/usr/bin/python高级
# -*- coding: UTF-8 -*-
import requests

url = 'http://aigc-dev.growknows.cn/api/logout'
headers = {'Host': 'aigc-dev.growknows.cn',
           'Connection': 'keep-alive',
           'sec-ch-ua': '"Not/A)Brand";v="99", "Microsoft Edge";v="115", "Chromium";v="115"',
           'sec-ch-ua-mobile': '?0',
           'Authorization': 'Bearer 35fc4d7483f64436ae7bf2814a0b61f0',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203',
           'Accept': 'application/json, text/plain, */*',
           'userId': '11',
           'user': 'maopeng',
           'sec-ch-ua-platform': '"Windows"',
           'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-Mode': 'cors',
           'Sec-Fetch-Dest': 'empty',
           'Referer': 'https://aigc-dev.growknows.cn/housing/home',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'}
test_case = {}

html = requests.get(url, headers=headers, verify=False)
print(len(html.text))
print(html.text)
