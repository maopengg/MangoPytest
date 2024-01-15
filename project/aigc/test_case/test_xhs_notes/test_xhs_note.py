# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 小红书笔记-剩余接口
# @Time   : 2023-08-23 16:02
# @Author : 毛鹏
import allure
import pytest

from models.api_model import ApiDataModel, CaseGroupModel
from models.models import AIGCDataModel
from project.aigc.modules.xhs_notes.note import NoteAPI
from tools.decorator.response import case_data
from tools.request_tool.case_tool import CaseTool


@allure.epic('AIGC')
@allure.feature('小红书')
@allure.story('2、小红书笔记模板生成页面其他接口')
class TestXHSNote(NoteAPI, CaseTool):
    data_model: AIGCDataModel = AIGCDataModel()

    @allure.title('1、笔记添加：不存在的关键词')
    @case_data(52)
    def test_xhs_note_01(self, data: ApiDataModel):
        name = self.random_goods_name_int()
        self.set_cache('keyword_name', name)
        data.test_case_data.case_json['name'] = name
        data, response_dict = self.case_run(self.api_note_add_keyword, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)
        if data.db_is_ass:
            delete_sel = f'DELETE FROM note_keyword WHERE id={response_dict["data"]["id"]} AND `name`="{name}";'
            self.data_model.mysql_obj.execute_delete(delete_sel)

    @allure.title('2、笔记添加：已存在的关键字')
    @case_data(149)
    def test_xhs_note_02(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_note_add_keyword, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('3、笔记添加：A账号已存在的关键字')
    @case_data(150)
    def test_xhs_note_03(self, data: ApiDataModel):
        name = self.random_goods_name_int()
        self.set_cache('keyword_name', name)
        data.test_case_data.case_json[0][data.test_case_data.case_step[0]]['name'] = name
        data.test_case_data.case_json[1][data.test_case_data.case_step[1]]['name'] = name
        with allure.step(data.test_case_data.case_step[0]):
            data, response_dict = self.case_run(self.api_note_add_keyword, data)
            self.case_ass(response_dict, data.test_case_data, data.db_is_ass, 0)
        with allure.step(data.test_case_data.case_step[1]):
            data.step = 1
            # 添加一个用例步骤进去，并且设置一个另外一个账号的headers
            case_group = CaseGroupModel()
            data.requests_list.append(case_group)
            case_group.request.headers = self.data_model.headers2

            data, response_dict = self.case_run(self.api_note_add_keyword, data)
            self.case_ass(response_dict, data.test_case_data, data.db_is_ass, 1)

    @allure.title('2、查询分类')
    @case_data(55)
    def test_xhs_note_2(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_note_query_classification, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('3、终止生成小红书笔记')
    @case_data(82)
    def test_xhs_note_3(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_note_stop, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)


if __name__ == '__main__':
    pytest.main(
        args=[
            r'D:\GitCode\APIAutoTest\project\aigc\test_case\creating_templates\test_note.py::TestNote::test_note_00::test_note_05'])
