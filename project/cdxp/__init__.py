# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-12 17:41
# @Author : 毛鹏
from config.settings import CDXP_CONFING_PATH
from enums.tools_enum import ProjectEnum
from project.cdxp.cdxp_data_model import CDXPDataModel
from tools.data_processor import CacheTool
from tools.files.read_yml import YmlReader
from tools.logging_tool.log_control import ERROR

project = ProjectEnum.CDXP.value


def preparation():
    file = YmlReader(CacheTool.get_cache(f'{project}_environment'), CDXP_CONFING_PATH)
    environment = file.get_environment()
    CDXPDataModel(host=environment.host, mysql_db=environment.mysql_db)


try:
    # CacheTool.set_cache(f'{project}_environment', 'test')
    preparation()
except Exception as e:
    ERROR.logger.error(f'{project}缓存设置失败:{e}')
