# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-10 10:26
# @Author : 毛鹏
import base64

import requests
from requests import Response

from modules.event.model import TrackModel, TrackSignup, ProfileSetModel
from tools.decorator.response import around
from tools.get_or_set_test_data import GetOrSetTestData


class EventAPI(GetOrSetTestData):

    @classmethod
    @around()
    def api_send_event(cls, data: TrackModel | TrackSignup | ProfileSetModel) -> Response:
        """
        事件上报接口
        :param data:
        :return:
        """
        response = requests.post(url=cls.get('event_url'), data=data)
        return response
