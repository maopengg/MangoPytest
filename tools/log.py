# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-10-25 21:46
# @Author : 毛鹏
from mangotools.log_collector import set_log

from settings.settings import IS_DEBUG
from tools import project_dir

log = set_log(project_dir.logs(), IS_DEBUG)
