# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-07-04 17:14
# @Author : 毛鹏
import json

from mangotools.data_processor import DataClean
from pydantic import BaseModel, ConfigDict


def json_serialize(data: str | None):
    try:
        if isinstance(data, str):
            return json.loads(data)
        else:
            return data
    except (json.decoder.JSONDecodeError, TypeError):
        return data


class OtherTestCaseModel(BaseModel):
    id: int
    project_name: str
    name: str
    data: dict | list[dict] | str | None = None
    other_data: dict | list[dict] | str | None = None
    ass_response_whole: dict | list[dict] | str | None = None

    @classmethod
    def get_obj(cls, data: dict):
        return cls(
            id=data['id'],
            project_name=data['project_name'],
            name=data['name'],
            data=json_serialize(data.get('data')),
            other_data=json_serialize(data.get('other_data')),
            ass_response_whole=json_serialize(data.get('ass_response_whole')),
        )


class OtherDataModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    test_case: OtherTestCaseModel  # 测试用例信息
    data_clean: DataClean = DataClean()  # 缓存数据
