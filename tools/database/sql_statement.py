# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-01-10 16:58
# @Author : 毛鹏
from tools.database.sqlite_handler import SQLiteHandler

sql_statement_1 = 'SELECT * FROM user_info;'
sql_statement_2 = f'INSERT INTO "user_info" ("username", "password", "ip", "port") VALUES (?, ?, ?, ?);'
sql_statement_3 = f'DELETE FROM user_info;'

if __name__ == '__main__':
    db_handler = SQLiteHandler()
    print(db_handler.execute_sql(sql_statement_1))
