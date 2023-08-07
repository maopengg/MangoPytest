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

    async def api_ago_dependency(self):
        """
        前置依赖
        @return:
        """

    async def api_after_dependency(self):
        """
        后置处理
        @return:
        """

    async def api_result_ass(self):
        """
        结果断言
        @return:
        """

    async def api_after_empty(self):
        """
        后置数据清除
        @return:
        """

    async def public_login(self, key, request: RequestModel):
        """
        处理登录token
        @return:
        """
        session = aiohttp.ClientSession()
        response = await HTTPRequest.http_post(session=session,
                                               url=request.url,
                                               headers=request.header,
                                               data=eval(
                                                   await self.replace_text(request.body)) if request.body else None)
        await self.set(key, await self.get_json_path_value(await response[0].json(), '$.access_token'))
        INFO.logger.info(f'公共参数Token设置成功：{await self.get(key)}')
        await session.close()

    async def public_header(self, key, header):
        """
        处理接口请求头
        @param key: 缓存key
        @param header: header
        @return:
        """
        await self.set(key, await self.replace_text(header))
        INFO.logger.info(f'公共参数请求头设置成功：{await self.get(key)}')

    async def public_ago_sql(self, key, sql):
        """
        处理前置sql
        @return:
        """
        sql = await self.replace_text(sql)
        my: MysqlDB = MysqlDB()
        await my.connect(await self.get('mysql'))
        sql_res_list = await my.select(sql)
        k_list = []
        for sql_res_dict in sql_res_list:
            for k, v in sql_res_dict.items():
                await self.set(f'{key}_{k}', v)
                k_list.append(k)
        for i in k_list:
            INFO.logger.info(f'公共参数sql设置成功：{await self.get(f"{key}_{i}")}')

    async def public_customize(self, key, value):
        """
        自定义参数
        @return:
        """
        await self.set(key, value)
        INFO.logger.info(f'公共参数自定义设置成功：{await self.get(key)}')
