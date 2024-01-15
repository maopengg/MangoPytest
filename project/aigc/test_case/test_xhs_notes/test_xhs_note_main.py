# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 小红书笔记-服饰达人&配饰达人&家具达人&检查达人-主流程
# @Time   : 2023-08-23 16:02
# @Author : 毛鹏
import allure
import pytest

from models.api_model import ApiDataModel
from project.aigc.modules.creating_templates.model import ResponseModel, NoteRequestModel
from project.aigc.modules.xhs_notes.note import NoteAPI
from tools.decorator.response import case_data
from tools.request_tool.case_tool import CaseTool


@allure.epic('AIGC')
@allure.feature('小红书')
@allure.story('1、小红书笔记模板生成主流程')
class TestXHSNoteMain(NoteAPI, CaseTool):

    @pytest.mark.run(1)
    @allure.title('1、服饰达人-查询关键词')
    @case_data(56)
    def test_note_01(self, data: ApiDataModel):
        """服饰达人的获取文章名称和文章内容"""
        data, response_dict = self.case_run(self.api_note_dress, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)
        result = ResponseModel(**response_dict)
        self.set_cache('test_note_01', result)

    @pytest.mark.run(2)
    @allure.title('2、服饰达人-生成小红书标题')
    @case_data(61)
    def test_note_02(self, data: ApiDataModel):
        result = self.get_cache('test_note_01')
        theme_directionr = result.data[0].name  # 选购攻略
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
        data.requests_list[0].request.json_data = note_data.dict()
        self.set_cache('test_note_011_note_data', note_data)
        data, response_dict = self.case_run(self.api_note_dress_title, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass, 1)
        nete_result = ResponseModel(**response_dict)
        self.set_cache('test_note_011', nete_result)

    @pytest.mark.run(3)
    @allure.title('3、服饰达人-生成小红书内容')
    @case_data(62)
    def test_note_03(self, data: ApiDataModel):
        nete_result = self.get_cache('test_note_011')
        note_data: NoteRequestModel = self.get_cache('test_note_011_note_data')
        note_data.title = self.json_loads(nete_result.data).get('message').get('1')
        note_data.request_id = self.generate_random_string(10)
        data.requests_list[0].request.json_data = note_data.dict()
        data, response_dict = self.case_run(self.api_note_article, data)
        assert response_dict is not None

    @pytest.mark.run(4)
    @allure.title('4、配饰达人-查询关键词')
    @case_data(57)
    def test_note_04(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_note_dress, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @pytest.mark.run(5)
    @allure.title('5、配饰达人-生成小红书标题')
    @case_data(63)
    def test_note_05(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_note_dress_title, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @pytest.mark.run(6)
    @allure.title('6、配饰达人-生成小红书内容')
    @case_data(64)
    def test_note_06(self, data: ApiDataModel):
        data.test_case_data.case_json['request_id'] = self.generate_random_string(10)
        data, response_dict = self.case_run(self.api_note_article, data)
        assert response_dict is not None

    @pytest.mark.run(7)
    @allure.title('7、家具达人-查询关键词')
    @case_data(58)
    def test_note_07(self, data: ApiDataModel):
        """服饰达人的获取文章名称和文章内容"""
        data, response_dict = self.case_run(self.api_note_dress, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @pytest.mark.run(8)
    @allure.title('8、家具达人-生成小红书标题')
    @case_data(65)
    def test_note_08(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_note_dress_title, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @pytest.mark.run(9)
    @allure.title('9、家具达人-生成小红书内容')
    @case_data(66)
    def test_note_09(self, data: ApiDataModel):
        data.test_case_data.case_json['request_id'] = self.generate_random_string(10)
        data, response_dict = self.case_run(self.api_note_article, data)
        assert response_dict is not None

    @pytest.mark.run(10)
    @allure.title('10、建材达人-查询关键词')
    @case_data(59)
    def test_note_10(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_note_dress, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @pytest.mark.run(11)
    @allure.title('11、建材达人-生成小红书标题')
    @case_data(67)
    def test_note_11(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_note_dress_title, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @pytest.mark.run(12)
    @allure.title('12、建材达人-生成小红书内容')
    @case_data(68)
    def test_note_12(self, data: ApiDataModel):
        data.test_case_data.case_json['request_id'] = self.generate_random_string(10)
        data, response_dict = self.case_run(self.api_note_article, data)
        assert response_dict is not None



if __name__ == '__main__':
    pytest.main(
        args=[
            r'D:\GitCode\APIAutoTest\project\aigc\test_case\creating_templates\test_note.py::TestNote::test_note_00::test_note_05'])
