# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-10-25 21:46
# @Author : 毛鹏
from settings.settings import IS_DEBUG
from tools import InitPath

log = set_log(InitPath.logs_dir, IS_DEBUG)