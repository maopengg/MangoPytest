# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-04-02 9:48
# @Author : 毛鹏
import numpy as np
from pandas.core.frame import DataFrame

from core.exceptions import *
from core.sources.feishu.document_data import DocumentData


class SourcesData:
    ui_element: DataFrame = None
    r = DocumentData()

    @classmethod
    def get_ui_element(cls, is_dict=True, **kwargs):
        if cls.ui_element is None:
            cls.ui_element = cls.r.ui_element().replace({np.nan: None})
        return cls.get(cls.ui_element, is_dict, **kwargs)

    @classmethod
    def get(cls, df: DataFrame, is_dict: bool, **kwargs) -> list[dict] | dict | None:
        conditions = None
        for key, value in kwargs.items():
            if isinstance(value, list):
                condition = df[key].isin(value)
            else:
                condition = df[key] == value
            if conditions is None:
                conditions = condition
            else:
                conditions = conditions & condition

        result = df[conditions]
        if result.empty:
            raise ToolsError(*ERROR_MSG_0349, value=(str(kwargs),))
        elif len(result) == 1:
            data = result.squeeze().to_dict()
        else:
            data = result.to_dict(orient="records")
        if isinstance(data, list) and is_dict:
            raise ToolsError(*ERROR_MSG_0348, value=(str(kwargs),))
        elif isinstance(data, list) and not is_dict:
            return data
        elif isinstance(data, dict) and is_dict:
            return data
        elif isinstance(data, dict) and not is_dict:
            return [
                data,
            ]


if __name__ == "__main__":
    api_info_dict = SourcesData.get_ui_element(id=1)
    print(api_info_dict)
