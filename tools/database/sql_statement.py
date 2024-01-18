# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-01-10 16:58
# @Author : 毛鹏
from tools.database.sqlite_handler import SQLiteHandler

sql_statement_1 = 'SELECT * FROM project where id = ? and is_notice = ?;'
sql_statement_2 = 'SELECT * FROM notice_config where project_id = ?;'
sql_statement_3 = 'select * FROM test_case WHERE id = ?;'

if __name__ == '__main__':
    db_handler = SQLiteHandler()
    print(db_handler.execute_sql(sql_statement_1, (1, 0)))
