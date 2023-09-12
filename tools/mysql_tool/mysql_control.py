# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-03-07 8:24
# @Author : 毛鹏
import pymysql

from models.tools_model import MysqlDBModel


class MySQLHelper:

    def __init__(self, db_data: MysqlDBModel):
        self.connection = pymysql.connect(
            host=db_data.host,
            port=db_data.port,
            user=db_data.user,
            password=db_data.password,
            database=db_data.database,
            cursorclass=pymysql.cursors.DictCursor

        )

    def execute_query(self, query):
        """
        查询数据
        :param query: sql
        :return:
        """
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def execute_update(self, query):
        """
        修改数据
        :param query: sql
        :return:
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()
        cursor.close()

    def close(self):
        """
        关闭连接
        :return:
        """
        self.connection.close()


if __name__ == '__main__':
    helper = MySQLHelper('localhost', 3306, 'root', 'password', 'mydatabase')
    insert_query = "INSERT INTO mytable (name, age) VALUES ('John', 25)"
    helper.execute_update(insert_query)
    select_query = "SELECT * FROM mytable"
    result = helper.execute_query(select_query)
    print(result)
    update_query = "UPDATE mytable SET age = 30 WHERE name = 'John'"
    helper.execute_update(update_query)
    delete_query = "DELETE FROM mytable WHERE name = 'John'"
    helper.execute_update(delete_query)
    helper.close()
