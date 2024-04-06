# -*- coding: utf-8 -*-
# @Project: MangoServer
# @Description: 
# @Time   : 2024-03-17 19:10
# @Author : 毛鹏

from pydantic_core._pydantic_core import ValidationError

from auto_test.project_enum import ProjectTypePaths
from enums.tools_enum import EnvironmentEnum, StatusEnum
from exceptions.error_msg import *
from exceptions.ui_exception import UiInitialError
from models.tools_model import MysqlConingModel
from sources import SourcesData
from tools.database.mysql_connect import MysqlConnect
from tools.logging_tool import logger


class ProjectPublicMethods:

    @staticmethod
    def get_project_test_object(
            project_name: str,
            test_environment: EnvironmentEnum) -> tuple[EnvironmentEnum, dict, dict]:
        project_type_paths = ProjectTypePaths()
        project_dict = project_type_paths.data[project_name]
        logger.debug(f'类ID：{id(project_type_paths)}')
        if project_dict.get('test_environment') is None:
            test_environment: EnvironmentEnum = test_environment
            logger.warning(f'项目：{project_name}未获取到测试环境变量，请检查！')
        else:
            test_environment: EnvironmentEnum = project_dict.get('test_environment')
        project: dict = SourcesData \
            .get_project(**{'name': project_name})
        test_object = SourcesData \
            .get_test_object(**{'project_id': project.get('id'), 'type': test_environment.value})
        return test_environment, project, test_object

    @staticmethod
    def get_mysql_info(test_object: dict) -> tuple[MysqlConingModel, MysqlConnect] | tuple[None, None]:
        mysql_config_model = None
        mysql_connect = None
        try:
            mysql_config_model = MysqlConingModel(host=test_object.get('db_host'),
                                                  port=test_object.get('db_port'),
                                                  user=test_object.get('db_user'),
                                                  password=test_object.get('db_password'),
                                                  database=test_object.get('db_database'))
            mysql_connect = MysqlConnect(mysql_config_model)

        except ValidationError:
            if test_object.get('is_db') == StatusEnum.SUCCESS.value:
                raise UiInitialError(*ERROR_MSG_0333)

        return mysql_config_model, mysql_connect
