#!/usr/bin/python高级
# -*- coding: UTF-8 -*-
import requests

url = 'http://jira.zalldigital.cn/rest/issueNav/1/issueTable'
headers = {'Host': 'jira.zalldigital.cn', 'Proxy-Connection': 'keep-alive', 'Content-Length': '171', 'Accept': '*/*',
           '__amdModuleName': 'jira/issue/utils/xsrf-token-header', 'X-Requested-With': 'XMLHttpRequest',
           'X-Atlassian-Token': 'no-check',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Origin': 'http://jira.zalldigital.cn',
           'Referer': 'http://jira.zalldigital.cn/issues/?filter=12022', 'Accept-Encoding': 'gzip, deflate',
           'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'}
cookies = {'JSESSIONID': '26CAD30F66F47415F9FCDAD05088509A',
           'atlassian.xsrf.token': 'BH46-DCX6-SSKZ-DYQZ_b23bbb266e62cc034dc5c112686032f59b556f73_lin'}
test_case = {'startIndex': '0', 'filterId': '12022',
             'jql': r'project = AIGCPRD AND issuetype in (Bug, 特性缺陷) AND created >= 2023-12-11 AND created <= 2024-01-07 order by created DESC',
             'layoutKey': 'list-view'}

html = requests.post(url, headers=headers, cookies=cookies, data=test_case)
print(html.json())
