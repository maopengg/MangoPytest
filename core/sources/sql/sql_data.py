import pandas
from mangotools.database import SQLiteConnect

from exceptions import *
from tools import project_dir

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


class SqlData:

    def __init__(self):
        self.sql_connect = SQLiteConnect(fr'{project_dir.root_path()}\sources\sql\data_storage.db')

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
