# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-03-17 19:10
# @Author : 毛鹏
from mangokit import MysqlConnect, MysqlConingModel
from pydantic_core._pydantic_core import ValidationError

from enums.tools_enum import StatusEnum, AutoTestTypeEnum
from exceptions.error_msg import *
from exceptions.ui_exception import UiInitialError
from models.api_model import ApiBaseDataModel
from models.ui_model import UiBaseDataModel
from sources import SourcesData
from tools.log import log
from tools.project_path.project_path import ProjectPaths


class ProjectPublicMethods:

    @staticmethod
    def get_project_test_object(project_name: str, ) -> tuple[int, dict, dict]:
        # 从共享的字典中获取实例
        try:
            project_dict = ProjectPaths.check()[project_name]
        except KeyError:
            ProjectPaths.init()
            project_dict = ProjectPaths.check()[project_name]

        if project_dict.get('test_environment') is None:
            project: dict = SourcesData \
                .get_project(**{'name': project_name})
            test_object = SourcesData \
                .get_test_object(**{'project_name': project.get('name'), 'is_use': 1})
            test_environment: int = test_object.get('type')
            log.warning(f'项目：{project_name}未获取到测试环境变量，请检查！')
        else:
            test_environment: int = project_dict.get('test_environment')
            project: dict = SourcesData \
                .get_project(**{'name': project_name})
            test_object = SourcesData \
                .get_test_object(**{'project_name': project.get('name'), 'type': test_environment})
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

    @classmethod
    def get_data_model(cls, model, project_enum, _type: AutoTestTypeEnum):
        test_environment, project, test_object = cls.get_project_test_object(project_name=project_enum.NAME.value)
        mysql_config_model, mysql_connect = cls.get_mysql_info(test_object)
        if _type == AutoTestTypeEnum.API:
            return model(
                test_environment=test_environment,
                base_data_model=ApiBaseDataModel(
                    test_object=test_object,
                    project=project,
                    host=test_object.get('host'),
                    is_database_assertion=bool(test_object.get('is_db')),
                    mysql_config_model=mysql_config_model,
                    mysql_connect=mysql_connect,
                )
            )
        else:
            return model(
                test_environment=test_environment,
                base_data_model=UiBaseDataModel(
                    test_object=test_object,
                    project=project,
                    host=test_object.get('host'),
                    is_database_assertion=bool(test_object.get('is_db')),
                    mysql_config_model=mysql_config_model,
                    mysql_connect=mysql_connect,
                )
            )
