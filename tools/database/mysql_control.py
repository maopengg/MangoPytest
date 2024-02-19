# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-03-07 8:24
# @Author : 毛鹏
import pymysql

from models.tools_model import MysqlConingModel


class MySQLConnect:

    def __init__(self, db_data: MysqlConingModel):
        self.connection = pymysql.connect(
            host=db_data.host,
            port=db_data.port,
            user=db_data.user,
            password=db_data.password,
            database=db_data.database,
            cursorclass=pymysql.cursors.DictCursor

        )

    def __del__(self):
        self.close()

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

    def execute_delete(self, query):
        """
        删除数据
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
    TEST_AIGC_MYSQL: MySQLHelper = MySQLHelper(
        MysqlConingModel(host='61.183.9.60', port=23306, user='root', password='zALL_mysql1', database='aigc'))
    print(TEST_AIGC_MYSQL.execute_query('select `status` from sync_log ORDER BY create_time DESC LIMIT 1;'))
