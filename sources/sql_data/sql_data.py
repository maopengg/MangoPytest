import pandas
from mangokit import SQLiteConnect

from exceptions import *
from tools import InitPath
from tools.sql_statement import *


class SqlData:

    def __init__(self):
        self.sql_connect = SQLiteConnect(fr'{InitPath.sqlite_dir}\data_storage.db')

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
            data = self.sql_connect.execute(sql)
        except IndexError:
            raise ToolsError(*ERROR_MSG_0331)
        return pandas.DataFrame(data)


if __name__ == '__main__':
    print(SqlData().project())
