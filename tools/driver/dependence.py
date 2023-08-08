# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 解决接口的依赖关系
# @Time   : 2022-11-10 21:24
# @Author : 毛鹏

import aiohttp
from tools.mysql.mysql_control import MysqlDB

from models.api_model import RequestModel
from tools.logging_tool.log_control import INFO
from tools.testdata import GetOrSetTestData


class Dependence(GetOrSetTestData):

    def api_ago_dependency(self):
        """
        前置依赖
        @return:
        """

    def api_after_dependency(self):
        """
        后置处理
        @return:
        """

    def api_result_ass(self):
        """
        结果断言
        @return:
        """

    def api_after_empty(self):
        """
        后置数据清除
        @return:
        """

    def public_login(self, key, request: RequestModel):
        """
        处理登录token
        @return:
        """
        session = aiohttp.ClientSession()
        response = HTTPRequest.http_post(session=session,
                                         url=request.url,
                                         headers=request.header,
                                         data=eval(
                                             self.replace_text(request.body)) if request.body else None)
        self.set(key, self.get_json_path_value(response[0].json(), '$.access_token'))

    INFO.logger.info(f'公共参数Token设置成功：{self.get(key)}')
    session.close()


def public_header(self, key, header):
    """
    处理接口请求头
    @param key: 缓存key
    @param header: header
    @return:
    """
    self.set(key, self.replace_text(header))


INFO.logger.info(f'公共参数请求头设置成功：{self.get(key)}')


def public_ago_sql(self, key, sql):
    """
    处理前置sql
    @return:
    """
    sql = self.replace_text(sql)
    my: MysqlDB = MysqlDB()
    my.connect(self.get('mysql'))


sql_res_list = my.select(sql)
k_list = []
for sql_res_dict in sql_res_list:
    for k, v in sql_res_dict.items():
        self.set(f'{key}_{k}', v)
    k_list.append(k)
for i in k_list:
    INFO.logger.info(f'公共参数sql设置成功：{self.get(f"{key}_{i}")}')


def public_customize(self, key, value):
    """
    自定义参数
    @return:
    """
    self.set(key, value)


INFO.logger.info(f'公共参数自定义设置成功：{self.get(key)}')
