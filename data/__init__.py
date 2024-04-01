# -*- coding: utf-8 -*-
# @Project: MangoServer
# @Description: 
# @Time   : 2024-04-01 20:59
# @Author : 毛鹏
from data.get_project_info import ProjectInfoApi

r = ProjectInfoApi()
r.main()
print(r.project)
print(r.notice_config)
print(r.test_object)
print(r.api_info)
print(r.api_test_case)
print(r.ui_element)
