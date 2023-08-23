# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-23 10:54
# @Author : 毛鹏
from config.settings import AIGC_CONFING_PATH
from enums.tools_enum import ProjectEnum
from tools.data_processor import CacheTool
from tools.files.read_yml import YmlReader
from tools.logging_tool.log_control import ERROR

project = ProjectEnum.AIGC.value


def preparation():
    file = YmlReader(CacheTool.cache_get(f'{project}_environment'), AIGC_CONFING_PATH)
    environment = file.get_environment()
    CacheTool.cache_set(f'{project}_host', environment.host)
    CacheTool.cache_set(f'{project}_headers', environment.headers)
    CacheTool.cache_set(f'{project}_mysql_db', environment.mysql_db)
    CacheTool.cache_set(f'{project}_headers', environment.notification_type_list)


try:
    # CacheTool.cache_set(f'{project}_environment', 'test')
    preparation()
except Exception as e:
    ERROR.logger.error(f'{project}缓存设置失败:{e}')
