#!/usr/bin/python高级
# -*- coding: UTF-8 -*-
import requests

url = 'https://www.chinabidding.cn/agency.info.Fbxx/list?keyword=&type=null&status=null&sign=&sort=desc&page=1&size=10'
headers = {'Host': 'www.chinabidding.cn', 'Connection': 'keep-alive', 'Content-Length': '61',
           'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
           'Accept': 'application/json, text/plain, */*', 'Content-Type': 'application/x-www-form-urlencoded',
           'sec-ch-ua-mobile': '?0',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.62',
           'sec-ch-ua-platform': '"Windows"', 'Origin': 'https://www.chinabidding.cn', 'Sec-Fetch-Site': 'same-origin',
           'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty',
           'Referer': 'https://www.chinabidding.cn/public/bidagency/index.html', 'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'}
cookies = {'acw_tc': '2760820516933151593603096e38a7be58658d1471b67710265fa6de1e6a41', 'banOrder': '0',
           'browser_id': '-848057161', 'Hm_lvt_ebcee0764883fb81bcdd54df18970c94': '1693315168',
           'gr_user_id': 'ea91e4a8-024a-481c-8ace-c68964cf7940',
           'b5897e326c6777f3_gr_session_id': 'df0ac059-f95c-4fab-b973-834244ebfc56',
           'b5897e326c6777f3_gr_session_id_sent_vst': 'df0ac059-f95c-4fab-b973-834244ebfc56',
           'Hm_lpvt_ebcee0764883fb81bcdd54df18970c94': '1693315204', 'pop_status': '1',
           'b5897e326c6777f3_gr_last_sent_sid_with_cs1': 'df0ac059-f95c-4fab-b973-834244ebfc56',
           'b5897e326c6777f3_gr_last_sent_cs1': '7927182', 'b5897e326c6777f3_gr_cs1': '7927182',
           'CBL_SESSION': '135090e56414fe45492dbadc1d73336028fbc8b3-___TS', 'CBL_ERRORS': ''}
test_case = {'keyword': '', 'type': 'null', 'status': 'null', 'sign': '', 'sort': 'desc', 'page': '1', 'size': '10'}

html = requests.post(url, headers=headers, cookies=cookies, json=test_case)
print(len(html.text))
print(html.text)
