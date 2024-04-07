# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-01-10 16:58
# @Author : 毛鹏

sql_statement_1 = 'SELECT * FROM ui_element where project_id = ? and module_name = ?;'
sql_statement_2 = 'SELECT * FROM project WHERE `name` = ?;'
sql_statement_3 = 'SELECT * FROM test_object WHERE `project_id` = ? AND type = ?;'
sql_statement_4 = 'SELECT * FROM api_test_case WHERE `id` = ?;'
sql_statement_5 = 'SELECT * FROM project WHERE `name` = ?;'
sql_statement_6 = 'SELECT * FROM notice_config WHERE `project_id` = ?;'
sql_statement_7 = 'SELECT * FROM api_info WHERE `id` = ?;'

sql_project = 'SELECT * FROM project;'
sql_test_object = 'SELECT * FROM test_object;'
sql_notice_config = 'SELECT * FROM notice_config;'
sql_api_info = 'SELECT * FROM api_info;'
sql_api_test_case = 'SELECT * FROM api_test_case;'
sql_ui_element = 'SELECT * FROM ui_element;'
