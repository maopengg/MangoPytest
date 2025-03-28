# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: # @Time   : 2023-03-11 17:25
# @Author : 毛鹏
from typing import Optional

from time import sleep
from uiautomator2 import Device

from models.ui_model import AndroidConfigModel
from tools.log import log

"""
python -m uiautomator2 init
python -m weditor

"""


class AndroidBase:

    def __init__(self, android_config: AndroidConfigModel):
        self.android_config = android_config
        self.android: Optional[Device] = None
        self.android.implicitly_wait(10)
        self.package = None

    def a_sleep(self, time_: int):
        """强制等待"""
        sleep(time_)

    def new_android(self):
        self.android = Device(self.android_config.equipment)
        log.info(f'设备启动成功，设备信息：{self.android.info}')


class ElementNotFoundError(Exception):
    """元素获取失败"""


class ElementNotDisappearError(Exception):
    """元素消失失败"""
