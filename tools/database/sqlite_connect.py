import os
import sqlite3
from typing import Union

from tools import InitPath


class SQLiteConnect:

    def __init__(self):
        db_name = os.path.join(InitPath.sqlite_dir, 'data_storage.db')
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def execute_sql(self, sql_query: str, data: tuple = None) -> Union[list[dict], int]:
        if data:
            self.cursor.execute(sql_query, data)
        else:
            self.cursor.execute(sql_query)
        if sql_query.strip().split()[0].upper() == 'SELECT':
            rows = self.cursor.fetchall()
            column_names = [description[0] for description in self.cursor.description]
            result_list = [dict(zip(column_names, row)) for row in rows]
            return result_list
        elif sql_query.strip().split()[0].upper() in ['INSERT', 'UPDATE']:
            self.conn.commit()
            return self.cursor.rowcount
        elif sql_query.strip().split()[0].upper() == 'DELETE':
            self.conn.commit()
            return self.cursor.rowcount
        elif sql_query.strip().split()[0].upper() == 'CREATE':
            self.conn.commit()
            return self.cursor.rowcount
        else:
            raise Exception('sql语句错误')

    def close_connection(self) -> None:
        self.conn.close()

    def __del__(self):
        self.conn.close()


create_table_query1 = '''
CREATE TABLE "project" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "name" TEXT NOT NULL --  
);
'''
create_table_query2 = '''
CREATE TABLE "test_object" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "project_id" INTEGER NOT NULL, -- 项目id
  "type" INTEGER NOT NULL, -- 环境类型
  "name" TEXT NOT NULL, -- 测试环境名称
  "client_type" INTEGER NOT NULL, -- 端类型
  "host" TEXT NOT NULL, -- 环境域名
  "is_notice" INTEGER NOT NULL, -- 是否进行通知
  "db_c_status" INTEGER NOT NULL, -- 是否可执行查询
  "db_rud_status" INTEGER NOT NULL, -- 是否可执行crud
  "db_user" TEXT, -- 数据库用户名
  "db_host" TEXT, -- 数据库IP
  "db_port" TEXT, -- 数据库端口
  "db_password" TEXT, -- 数据库密码
  "db_database" TEXT -- 主库
);
'''
create_table_query3 = '''
CREATE TABLE "notice_config" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "project_id" INTEGER NOT NULL, -- 项目id
  "type" INTEGER NOT NULL, -- 通知类型
  "config" TEXT NOT NULL -- 通知配置
);
'''
create_table_query4 = '''
CREATE TABLE "api_test_case" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "project_id" INTEGER NOT NULL, -- 项目id
  "name" TEXT NOT NULL, -- 接口名称
  "params" TEXT, -- 接口参数
  "data" TEXT, -- 接口请求数据
  "json" TEXT, -- 接口请求json
  "file" TEXT, -- 接口请求文件
  "other_data" TEXT, -- 其他请求数据
  "ass_response_whole" TEXT, -- 请求全匹配断言
  "ass_response_value" TEXT, -- 请求响应断言
  "ass_sql" TEXT, -- sql断言
  "front_sql" TEXT, -- 前置sql
  "posterior_sql" TEXT, -- 后置sql
  "posterior_response" TEXT, -- 后置响应结果提取
  "dump_data" TEXT -- 后置数据清除
);
'''
create_table_query5 = '''
CREATE TABLE "ui_element" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "project_id" INTEGER NOT NULL, -- 项目id
  "module_name" INTEGER NOT NULL, -- 项目id
  "page_name" INTEGER NOT NULL, -- 项目id
  "ele_name" TEXT NOT NULL, -- 元素名称
  "method" INTEGER NOT NULL, -- method
  "locator" TEXT NOT NULL, -- 选择器
  "nth" INTEGER, -- 下标
  "sleep" INTEGER -- 等等时间
);
'''
create_table_query6 = '''
CREATE TABLE "api_info" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "project_id" INTEGER NOT NULL, -- 项目id
  "name" TEXT NOT NULL, -- 接口名称
  "client_type" INTEGER NOT NULL, -- 接口端类型
  "method" INTEGER NOT NULL, -- 接口请求方法
  "url" TEXT NOT NULL, -- url
  "headers" TEXT-- url
);
'''

db_handler = SQLiteConnect()
for i in [create_table_query1, create_table_query2, create_table_query3, create_table_query4, create_table_query5,
          create_table_query6]:
    try:
        db_handler.execute_sql(i)
    except sqlite3.OperationalError:
        pass
# 关闭连接
db_handler.close_connection()
