# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-01-10 16:58
# @Author : 毛鹏
from tools.database.sqlite_connect import SQLiteConnect

sql_statement_1 = 'SELECT * FROM ui_element where project_id = ? and module_name = ?;'
sql_statement_2 = 'SELECT * FROM project WHERE `name` = ?;'
sql_statement_3 = 'SELECT * FROM test_object WHERE `project_id` = ? AND type = ?;'
sql_statement_4 = 'SELECT * FROM api_test_case WHERE `id` = ?;'
sql_statement_5 = 'SELECT * FROM project WHERE `name` = ?;'
sql_statement_6 = 'SELECT * FROM notice_config WHERE `project_id` = ?;'
if __name__ == '__main__':
    db_handler = SQLiteConnect()
    print(db_handler.execute_sql(sql_statement_1, (1, 0)))
