# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-11 11:08
# @Author : 毛鹏

# ↓*************************************表名称对应ID*************************************↓
API_INFO = ("LntEsBf88h8KDXtjmKNcHgwSnoc", [{"sheet_id": "ef820e", "title": "Sheet1"}])
API_TEST_CASE = ("XLcrsEVLkhdDQvtWaJQc4uennvb", [{"sheet_id": "e8f425", "title": "Sheet1"}])
PROJECT = ("StFhs7b34h410ktn4FBc9qJsn8e", [{"sheet_id": "8d41b9", "title": "项目信息"},
                                           {"sheet_id": "58AgAa", "title": "通知配置"},
                                           {"sheet_id": "RwlKtG", "title": "测试环境"}])
UI_ELEMENT = ("ZQfZsC7IShpkGytZLoKc1gbXnPS", [{"sheet_id": "9f326e", "title": "Sheet1"}])

# 是否开启日志打印
PRINT_EXECUTION_RESULTS = True
# 请求超时失败时间
REQUEST_TIMEOUT_FAILURE_TIME = 60
# 是否开启UI自动化浏览器全屏
BROWSER_IS_MAXIMIZE = True
# 邮件配置
EMAIL_HOST = 'smtp.qq.com'
SEND_USER = '729164035@qq.com'
STAMP_KEY = 'lqfzvjbpfcwtbecg'

# 代理地址，如果没有就是空字典
PROXY = {'http': '127.0.0.1:7890', 'https': '127.0.0.1:7890'}

if __name__ == '__main__':
    print("proxy".upper())
    print(API_TEST_CASE[1][0].get('sheet_id'))
