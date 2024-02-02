# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-01-18 16:30
# @Author : 毛鹏
import requests
url = "https://www.jianguoyun.com/d/ajax/userop/getMetering"
header = {
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.jianguoyun.com",
    "Referer": "https://www.jianguoyun.com/d/home",
    "Cookie": "referrer=https://www.jianguoyun.com/; page_locale=zh; umn=729164035%40qq.com; ta=oKbl495OGIF7htQDjQDSe2ccT%2BeqVk9yauqwWOMiptw%3D"
}

res = requests.get(url, headers=header)
print(res.text)

res1 = requests.get("https://www.jianguoyun.com/c/tblv2/UKhhJVNMde9_6uSFzCTXMkJVWLoGOxwiBhFNlAWB8qrRhGVnJ0A8h45gtq6JdkS8OrXKKI9Q/PNK0r6a-HI-KtEoUtaI1uYEd8xRjhRpoRyXhG7yl7sA/l")
print(res1.text)
res2 = requests.post("https://www.jianguoyun.com/d/ajax/fileops/uploadXHRV2?path=%2F&dirName=%2F&sndId=18b5ecc&sndMagic=522b74dd51ae8a98&name=%E8%AF%A6%E6%83%85-09.jpg",headers=header)
print(res2.text)
