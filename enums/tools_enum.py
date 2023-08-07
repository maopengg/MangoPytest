# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-07-04 13:42
# @Author : 毛鹏
from enum import Enum


class ClientTypeEnum(str, Enum):
    ACTUATOR = "actuator"
    WEB = "web"
    SERVER = "server"
