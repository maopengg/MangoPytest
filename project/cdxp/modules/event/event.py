# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-10 10:26
# @Author : 毛鹏

from requests import Response

from project.cdxp.modules.event.model import TrackModel, TrackSignup, ProfileSetModel
from tools.data_processor import DataProcessor
from tools.decorator.response import around
from tools.request_tool.request_tool import RequestTool


class EventAPI(DataProcessor, RequestTool):

    @classmethod
    @around('事件上报接口')
    def api_send_event(cls, data: TrackModel | TrackSignup | ProfileSetModel) -> tuple[Response, str, dict] | Response:
        """
        事件上报接口
        :param data:
        :return:
        """
        response = cls.http_post(url=cls.get_cache('event_url'), data=data)
        return response, '', {}
