# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-12 17:41
# @Author : 毛鹏
# import requests
from pydantic import BaseModel

from auto_test import ApiBaseDataModel
from tools.decorator.singleton import singleton


#
@singleton
class CDPDataModel(BaseModel):
    test_environment: str
    user_info: dict = {'admin': {'username': 'maopeng@zalldigital.com', 'password': 'm729164035'}}
    headers: dict = {'Authorization': 'Basic d2ViQXBwOndlYkFwcA==', 'Accept': 'application/json, text/plain, */*'}
    base_data_model: ApiBaseDataModel
    cache_data: dict | None = None

#
# def cdp_login():
#     """
#     登录接口，获取通用token
#     :return:
#     """
#     cdp_dict = project_type_paths[CDPEnum.NAME.value]
#     if cdp_dict.get('test_environment') is None:
#         test_environment = 'pre'
#         WARNING.logger.warning(f'项目：{CDPEnum.NAME.value}未获取到测试环境变量，请检查！')
#     else:
#         test_environment = cdp_dict.get('test_environment')
#
#     try:
#         project: dict = SQLiteHandler().execute_sql(sql_statement_2, data=(CDPEnum.NAME.value,))[0]
#     except IndexError:
#         raise LoginError(*ERROR_MSG_0331)
#
#     try:
#         test_object: dict = SQLiteHandler().execute_sql(sql_statement_3, data=(project.get('id'),))[0]
#     except IndexError:
#         raise LoginError(*ERROR_MSG_0332)
#     mysql_config_model = None
#     mysql_connect = None
#     try:
#         mysql_config_model = MysqlConingModel(host=test_object.get('db_host'),
#                                               port=test_object.get('db_port'),
#                                               user=test_object.get('db_user'),
#                                               password=test_object.get('db_password'),
#                                               database=test_object.get('db_database'))
#     except ValidationError:
#         if test_object.get('is_db') == StatusEnum.SUCCESS.value:
#             raise LoginError(*ERROR_MSG_0333)
#     else:
#         mysql_connect = MySQLConnect(mysql_config_model)
#
#     data_model: CDPDataModel = CDPDataModel(
#         test_environment=test_environment,
#         base_data_model=ApiBaseDataModel(
#             test_object=test_object,
#             project=project,
#             host=test_object.get('host'),
#             is_database_assertion=True if test_object.get('is_db') == StatusEnum.SUCCESS.value else False,
#             mysql_config_model=mysql_config_model,
#             mysql_connect=mysql_connect,
#         )
#     )
#     for role, user in data_model.user_info.items():
#         password = EncryptionTool.md5_encrypt(user.get('password'))
#         login_url = f'{test_object.get("host")}/backend/api-auth/oauth/token?username={user.get("username")}&password={password}&grant_type=password_code'
#         response = requests.post(url=login_url, headers=data_model.headers)
#         try:
#             response_dict = response.json()
#         except AttributeError:
#             raise LoginError(*ERROR_MSG_0330, value=(response.json(),))
#         if role == 'admin':
#             user_info_url = f'{test_object.get("host")}/backend/api-user/users/current'
#             data_model.headers['Authorization'] = 'Bearer ' + response_dict['data']['access_token']
#             response = requests.get(url=user_info_url, headers=data_model.headers)
#             user_info_dict = response.json()
#             data_model.headers['Currentproject'] = 'precheck'
#             data_model.headers['Userid'] = str(user_info_dict["data"]["id"])
#             user_info_service_url = f'{test_object.get("host")}/backend/api-user/user/projects/{user_info_dict["data"]["id"]}'
#             response = requests.get(url=str(user_info_service_url), headers=data_model.headers)
#             user_info_service_dict = response.json()
#             data_model.headers['Service'] = user_info_service_dict['data'][0]['serviceName']
#             data_model.base_data_model.headers = data_model.headers
#
#     INFO.logger.info(f'{CDPEnum.NAME.value}的基础信息设置完成！')
#
#
# cdp_login()
