import pandas

from exceptions.error_msg import ERROR_MSG_0331
from exceptions.ui_exception import UiInitialError
from tools.database.sql_statement import sql_project, sql_test_object, sql_notice_config, sql_api_info, \
    sql_api_test_case, sql_ui_element
from tools.database.sqlite_connect import SQLiteConnect


class SqlData:

    def __init__(self):
        self.sql_connect = SQLiteConnect()

    def project(self):
        return self.cls(sql_project)

    def notice_config(self):
        return self.cls(sql_test_object)

    def test_object(self):
        return self.cls(sql_notice_config)

    def api_info(self):
        return self.cls(sql_api_info)

    def api_test_case(self):
        return self.cls(sql_api_test_case)

    def ui_element(self):
        return self.cls(sql_ui_element)

    def cls(self, sql):
        try:
            data = self.sql_connect.execute_sql(sql)
        except IndexError:
            raise UiInitialError(*ERROR_MSG_0331)
        return pandas.DataFrame(data)


if __name__ == '__main__':
    print(SqlData().project())
