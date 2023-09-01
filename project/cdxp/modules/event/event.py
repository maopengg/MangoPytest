# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-10 10:26
# @Author : 毛鹏

import requests
from requests import Response

from project.cdxp.modules.event.model import TrackModel, TrackSignup, ProfileSetModel
from tools.data_processor import DataProcessor
from tools.decorator.response import around


class EventAPI(DataProcessor):

    @classmethod
    @around('事件上报接口')
    def api_send_event(cls, data: TrackModel | TrackSignup | ProfileSetModel) -> tuple[Response, str, dict] | Response:
        """
        事件上报接口
        :param data:
        :return:
        """
        response = requests.post(url=cls.get_cache('event_url'), data=data)
        return response, '', {}
