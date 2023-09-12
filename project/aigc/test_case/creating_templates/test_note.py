# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-23 16:02
# @Author : 毛鹏
import allure
import pytest

from models.api_model import TestCaseModel
from project.aigc.modules.creating_templates.model import ResponseModel, NoteRequestModel
from project.aigc.modules.creating_templates.note import NoteAPI
from tools.decorator.response import testdata
from tools.logging_tool.log_control import INFO


@allure.epic('AIGC')
@allure.feature('创作模板')
@allure.story('小红书笔记')
class TestNote(NoteAPI):

    @allure.title('服饰达人生成')
    @testdata(5)
    def test_note_01(self, test_data: TestCaseModel):
        """服饰达人的获取文章名称和文章内容"""
        with allure.step('1.从创作模板进入到服饰达人中'):
            response = self.api_note_dress(2)
            result = ResponseModel(**response.json())
            assert result.status == 0
            assert result.data is not None
            assert result.data[0].name == '主题方向'
        with allure.step('2.选择下拉框的值点击生成标题'):
            theme_directionr = result.data[0].children[0].name  # 选购攻略
            plant = [result.data[1].children[0].children[0].dict()]
            target = [result.data[2].children[2].dict()]
            selling = [result.data[3].children[2].dict()]
            keyword = [result.data[4].children[1].children[2].dict()]
            note_data = NoteRequestModel(first_type='服饰配饰',
                                         user=self.data_model.headers.get('User'),
                                         user_id=self.data_model.headers.get('userId'),
                                         second_type='服饰',
                                         theme_direction=theme_directionr,
                                         product_names=[obj.get('name') for obj in plant],
                                         target_populations=[obj.get('name') for obj in target],
                                         selling_points=[obj.get('name') for obj in selling],
                                         other_keywords=[obj.get('name') for obj in keyword],
                                         details=self.json_dumps({"subject": theme_directionr,
                                                                  "plant": plant,
                                                                  "target": target,
                                                                  "selling": selling,
                                                                  "keyword": keyword}), )
            nete_response = self.api_note_dress_title(note_data)
            nete_result = ResponseModel(**nete_response.json())
            data: str = self.response_decoding(nete_result.data)
            INFO.logger.info(f'获取文章接口的msg内容：{data}')
            assert nete_result.data is not None
            assert nete_result.status == 0
        with allure.step('3.选择标题后生成文章'):
            note_data.title = self.json_loads(data).get('message').get('1')
            _response = self.api_note_article(note_data)
            _result = ResponseModel(**_response.json())
            INFO.logger.info(f'获取文章接口的msg内容：{self.response_decoding(_result.data)}')
            assert nete_result.data is not None
            assert nete_result.status == 0


if __name__ == '__main__':
    pytest.main(
        args=[r'D:\GitCode\APIAutoTest\project\aigc\test_case\creating_templates\test_note.py::TestNote::test_note01'])
