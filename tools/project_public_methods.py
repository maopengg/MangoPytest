# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-03-17 19:10
# @Author : 毛鹏
import json

import os

from mangokit import MysqlConnect, MysqlConingModel
from pydantic_core._pydantic_core import ValidationError

from enums.tools_enum import StatusEnum, AutoTestTypeEnum
from exceptions import *
from models.api_model import ApiBaseDataModel
from models.tools_model import CaseRunListModel
from models.ui_model import UiBaseDataModel
from sources import SourcesData
from tools.log import log


class ProjectPublicMethods:

    @staticmethod
    def get_project_test_object(project_name: str, _type: AutoTestTypeEnum) -> tuple[int, dict, dict]:
        # 从共享的字典中获取实例
        # try:
        #     project_dict = ProjectPaths.check()[project_name]
        # except (KeyError, FileNotFoundError):
        #     ProjectPaths.init()
        #     project_dict = ProjectPaths.check()[project_name]
        # os.environ['TEST_ENV'] = CaseRunListModel(**{"case_run":[{"project":"智投","type":1,"test_environment":1}]}).model_dump_json()
        project: dict = SourcesData.get_project(name=project_name)
        try:
            case_list = CaseRunListModel(**json.loads(os.environ['TEST_ENV']))
            test_object = None
            test_environment = None
            for i in case_list.case_run:
                if i.project.value == project_name and _type == i.type:
                    test_environment = i.test_environment.value
                    test_object = SourcesData.get_test_object(
                        project_name=project.get('name'),
                        type=i.test_environment.value
                    )
        except KeyError:
            test_object = SourcesData.get_test_object(project_name=project.get('name'), is_use=StatusEnum.SUCCESS.value)
            test_environment: int = test_object.get('type')
        if test_object is None or test_environment is None:
            log.error(f'项目:{project_name}没有可用的测试对象')
            raise ToolsError(*ERROR_MSG_0333)
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
                raise ToolsError(*ERROR_MSG_0333)

        return mysql_config_model, mysql_connect

    @classmethod
    def get_data_model(cls, model, project_enum, _type: AutoTestTypeEnum):
        test_environment, project, test_object = cls.get_project_test_object(project_enum.NAME.value, _type)
        mysql_config_model, mysql_connect = cls.get_mysql_info(test_object)
        if _type == AutoTestTypeEnum.API:
            return model(
                test_environment=test_environment,
                base_data=ApiBaseDataModel(
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
                base_data=UiBaseDataModel(
                    test_object=test_object,
                    project=project,
                    host=test_object.get('host'),
                    is_database_assertion=bool(test_object.get('is_db')),
                    mysql_config_model=mysql_config_model,
                    mysql_connect=mysql_connect,
                )
            )
