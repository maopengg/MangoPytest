# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:25
# @Author : 毛鹏
import requests
from requests.models import Response

from tools.decorator.response import around
from tools.testdata import GetOrSetTestData


class OverviewAPI(GetOrSetTestData):

    @classmethod
    @around()
    def api_check_state(cls) -> Response:
        """
        登录接口
        :return:
        """
        url = cls.get('host') + '/backend/api-data/model/config/heart/checkState'
        headers = cls.get('headers')
        print(type(headers))
        print(headers)
        return requests.get(url=url, headers=headers)

    @classmethod
    @around()
    def api_reset_password(cls) -> Response:
        """
        重置密码
        :return:
        """


if __name__ == '__main__':
    l = OverviewAPI()
    l.set('host', 'https://cdxppre.zalldata.cn/')
    l.set('headers', {
        'Authorization': 'Basic d2ViQXBwOndlYkFwcA==',
        'Accept': 'application/json, text/plain, */*',
        'service': 'zall',
        'currentProject': 'precheck',
        'userId': '201'})
    print(l.api_check_state().json())
