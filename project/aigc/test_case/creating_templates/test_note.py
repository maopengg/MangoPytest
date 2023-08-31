# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-23 16:02
# @Author : 毛鹏
import allure
import pytest

from project.aigc.modules.creating_templates.creating_templates import CreatingTemplatesAPI
from project.aigc.modules.creating_templates.model import ResponseModel
from tools.logging_tool.log_control import INFO


@allure.epic('AIGC')
@allure.feature('创作模板-小红书笔记')
class TestNote:

    @allure.story('服饰达人列表接口')
    def test_note_01(self):
        response = CreatingTemplatesAPI.api_note_dress()
        result = ResponseModel(**response.json())
        name = result.data[0].name
        INFO.logger.info(f'name:{name}')
        assert result.status == 0
        assert result.data is not None
        assert result.data[0].name == '主题方向'


if __name__ == '__main__':
    pytest.main(
        args=[r'D:\GitCode\APIAutoTest\project\aigc\test_case\creating_templates\test_note.py::TestNote::test_note01'])
