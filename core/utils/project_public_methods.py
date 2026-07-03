# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-03-17 19:10
# @Author : 毛鹏
import json
import os

from mangotools.database import MysqlConnect
from mangotools.models import MysqlConingModel
from pydantic_core._pydantic_core import ValidationError

from core.enums.tools_enum import PytestSystemEnum
from core.enums.tools_enum import StatusEnum, AutoTestTypeEnum, EnvironmentEnum
from core.exceptions import *


class InitBaseData:

    @classmethod
    def main(cls, project_name: str, _type: AutoTestTypeEnum):
        # 延迟导入以避免循环导入
        from core.models.tools_model import BaseDataModel, ProjectModel, TestObjectModel
        from core.sources import SourcesData
        
        project = cls.__project(project_name, SourcesData, ProjectModel)
        test_object, test_environment = cls.__test_object(project, _type, SourcesData, TestObjectModel)
        mysql_config_model, mysql_connect = cls.__mysql_conn(test_object)
        return BaseDataModel(
            test_environment=test_environment,
            test_object=test_object,
            project=project,
            mysql_config_model=mysql_config_model,
            mysql_connect=mysql_connect,
        )

    @classmethod
    def __project(cls, project_name: str, SourcesData, ProjectModel):
        return ProjectModel(**SourcesData.get_project(name=project_name))

    @classmethod
    def __test_object(cls, project, _type: AutoTestTypeEnum, SourcesData, TestObjectModel) -> tuple:
        # 延迟导入以避免循环导入
        from core.models.tools_model import CaseRunListModel
        
        try:
            case_list = CaseRunListModel(**json.loads(os.environ['TEST_ENV']))
            if case_list.case_run:
                test_environment = next(
                    (i.test_environment.value for i in case_list.case_run if
                     i.project.value == project.name and _type == i.type),
                    None
                )
                if test_environment is None:
                    raise ToolsError(*ERROR_MSG_0024)
                test_object = SourcesData.get_test_object(
                    project_name=project.name,
                    type=test_environment
                )
            else:
                raise ToolsError(*ERROR_MSG_0023)
        except KeyError:
            try:
                test_environment = int(os.environ.get(PytestSystemEnum.TEST_ENV.value))
                test_object = SourcesData.get_test_object(project_name=project.name, type=test_environment)
            except (KeyError, TypeError):
                test_object = SourcesData.get_test_object(project_name=project.name, is_use=StatusEnum.SUCCESS.value)
                test_environment = int(test_object.get('type'))

        return TestObjectModel(**test_object), EnvironmentEnum(test_environment)

    @classmethod
    def __mysql_conn(cls, test_object) -> tuple[MysqlConingModel, MysqlConnect] | tuple[None, None]:
        if test_object.db_c_status == StatusEnum.SUCCESS.value and test_object.db_rud_status == StatusEnum.SUCCESS.value:
            try:
                mysql_config_model = MysqlConingModel(host=test_object.db_host,
                                                      port=test_object.db_port,
                                                      user=test_object.db_user,
                                                      password=test_object.db_password,
                                                      database=test_object.db_database)
                mysql_connect = MysqlConnect(mysql_config_model)
                return mysql_config_model, mysql_connect
            except ValidationError:
                if test_object.db_c_status == StatusEnum.SUCCESS.value or test_object.db_rud_status == StatusEnum.SUCCESS.value:
                    raise ToolsError(*ERROR_MSG_0333)

        return None, None
