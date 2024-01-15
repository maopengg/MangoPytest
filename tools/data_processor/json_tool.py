# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-05-24 23:20
# @Author : 毛鹏
import json
from typing import IO

import jsonpath
import jsonpath_ng as jp
from tools.logging_tool.log_control import ERROR

class JsonTool:
    """json数据处理类"""

    @classmethod
    def json_load(cls, json_file: IO[str]) -> str:
        """
        将json文件转换成字符串
        :param json_file:
        :return:
        """
        return json.load(json_file)

    @classmethod
    def json_dump(cls, data: str, json_file: IO[str]) -> None:
        """
        将Python对象转换成json格式，并写入到json文件中
        :param data:
        :param json_file:
        :return:
        """
        json.dump(data, json_file)

    @classmethod
    def json_loads(cls, data: str) -> list | dict | None:
        """
        将json字符串转换为list或dict
        :param data:
        :return:
        """
        if data is None:
            return None
        return json.loads(data)

    @classmethod
    def json_dumps(cls, data: list | dict, indent=None) -> str:
        """
        将dict或list转换为json字符串
        :param data:
        :param indent:
        :return:
        """
        return json.dumps(data, indent=indent)

    @classmethod
    def json_flatten(cls, json_obj: list | dict, sep='_', prefix=''):
        """
        将嵌套的json对象展开成扁平的字典
        :param json_obj:
        :param sep:
        :param prefix:
        :return:
        """
        result = {}
        for key, value in json_obj.items():
            new_key = prefix + key
            if isinstance(value, dict):
                result.update(cls.json_flatten(value, sep, new_key + sep))
            else:
                result[new_key] = value
        return result

    @classmethod
    def json_get_path_value(cls, obj: dict | list, expr: str, index=0) -> str | list | dict| bool:
        """
        通过jsonpath取出对应的value
        @param obj: 需要取出的对象
        @param expr: 表达式
        @param index:下标
        @return:
        """
        try:
            value = jsonpath.jsonpath(obj, expr)
            return value[index]
        except TypeError as e:
            ERROR.logger.error(f"表达式未取到值{e}->对象：{obj}，表达式：{expr}，下标：{index}")
            return False

    @classmethod
    def json_is_valid_jsonpath(cls, variable: str):
        if variable.startswith("$"):
            try:
                jp.parse(variable)
                return True
            except jp.parser.ParserError:
                return False
        return False

    @classmethod
    def dict_to_sql_conditions(cls, dictionary: dict):
        conditions = []
        limit = ''
        for key, value in dictionary.items():
            if key != 'currentPage' and key != 'pageSize':
                if isinstance(value, str):
                    conditions.append(f"`{key}` like'%{value}%'")
                else:
                    conditions.append(f"`{key}`= {value}")
            if key == 'pageSize':
                limit = f"limit {value}"
        if len(conditions) > 0:
            return "and " + " and ".join(conditions) + limit
        else:
            return limit


if __name__ == '__main__':
    dat = {"status": 0, "message": None, "data": {"records": [{"createTime": "2023-08-30 14:28:54", "updateTime": "2023-09-20 16:25:34", "id": 19763, "brandId": 388, "brandName": "天白主播孵化", "accountId": "489883", "date": None, "unitId": None, "unitName": "客资收集_单元_20230822_101928", "projectName": None, "deliveryWay": "信息流", "product": "主播", "kolNote": "一日入门101928", "orientation": "新手", "deliveryWay2": "无", "targetPattern": "无", "status": 1}, {"createTime": "2023-08-30 14:28:54", "updateTime": "2023-08-30 14:37:24", "id": 19762, "brandId": 388, "brandName": "天白主播孵化", "accountId": "489883", "date": None, "unitId": None, "unitName": "客资收集_单元_20230822_102537", "projectName": None, "deliveryWay": "信息流", "product": "主播", "kolNote": "一日入门102537", "orientation": "新手", "deliveryWay2": "无", "targetPattern": "无", "status": 1}, {"createTime": "2023-08-30 14:28:54", "updateTime": "2023-08-30 14:37:50", "id": 19761, "brandId": 388, "brandName": "天白主播孵化", "accountId": "489883", "date": None, "unitId": None, "unitName": "客资收集_单元_20230823_140110", "projectName": None, "deliveryWay": "信息流", "product": "主播", "kolNote": "一日入门140110", "orientation": "新手", "deliveryWay2": "无", "targetPattern": "无", "status": 1}, {"createTime": "2023-08-30 14:28:54", "updateTime": "2023-08-30 14:38:21", "id": 19760, "brandId": 388, "brandName": "天白主播孵化", "accountId": "489883", "date": None, "unitId": None, "unitName": "客资收集_单元_20230825_114539", "projectName": None, "deliveryWay": "信息流", "product": "文艺主播", "kolNote": "入门速成114539", "orientation": "学生", "deliveryWay2": "无", "targetPattern": "无", "status": 1}, {"createTime": "2023-08-30 14:28:55", "updateTime": "2023-09-01 15:05:21", "id": 19789, "brandId": 402, "brandName": "柳丝木", "accountId": "486887", "date": None, "unitId": None, "unitName": "信商销-yaya-卸妆油-成单-0824", "projectName": None, "deliveryWay": "yaya", "product": "卸妆油", "kolNote": "成单", "orientation": "0824", "deliveryWay2": "1", "targetPattern": "1", "status": 1}, {"createTime": "2023-08-30 14:28:55", "updateTime": "2023-09-18 18:04:38", "id": 19781, "brandId": 402, "brandName": "柳丝木", "accountId": "486887", "date": None, "unitId": None, "unitName": "信商销-再熬夜就变秃头-隔离-成单-美妆-0824", "projectName": None, "deliveryWay": "再熬夜就变秃头", "product": "隔离", "kolNote": "成单", "orientation": "美妆", "deliveryWay2": "0824", "targetPattern": "wu", "status": 1}, {"createTime": "2023-08-30 14:28:55", "updateTime": None, "id": 19784, "brandId": 402, "brandName": "柳丝木", "accountId": "486887", "date": None, "unitId": None, "unitName": "信商销-可可有点口渴-卸妆油-成单-0824", "projectName": None, "deliveryWay": None, "product": None, "kolNote": None, "orientation": None, "deliveryWay2": None, "targetPattern": None, "status": 0}, {"createTime": "2023-08-30 14:28:55", "updateTime": None, "id": 19786, "brandId": 402, "brandName": "柳丝木", "accountId": "486887", "date": None, "unitId": None, "unitName": "信商销-哈密瓜味榴莲糖🍬-卸妆油-成单-0824", "projectName": None, "deliveryWay": None, "product": None, "kolNote": None, "orientation": None, "deliveryWay2": None, "targetPattern": None, "status": 0}, {"createTime": "2023-08-30 14:43:28", "updateTime": None, "id": 23600, "brandId": 402, "brandName": "柳丝木", "accountId": "486887", "date": None, "unitId": None, "unitName": "信商销-哈密瓜味榴莲糖🍬-卸妆油-成单-美妆-0824", "projectName": None, "deliveryWay": None, "product": None, "kolNote": None, "orientation": None, "deliveryWay2": None, "targetPattern": None, "status": 0}, {"createTime": "2023-08-30 14:28:55", "updateTime": None, "id": 19770, "brandId": 402, "brandName": "柳丝木", "accountId": "486887", "date": None, "unitId": None, "unitName": "信商销-小可-卸妆油-成单-美妆-0825", "projectName": None, "deliveryWay": None, "product": None, "kolNote": None, "orientation": None, "deliveryWay2": None, "targetPattern": None, "status": 0}, {"createTime": "2023-08-30 14:28:55", "updateTime": None, "id": 19774, "brandId": 402, "brandName": "柳丝木", "accountId": "486887", "date": None, "unitId": None, "unitName": "信商销-小春雪酱-卸妆油-成单-美妆-0825", "projectName": None, "deliveryWay": None, "product": None, "kolNote": None, "orientation": None, "deliveryWay2": None, "targetPattern": None, "status": 0}, {"createTime": "2023-08-30 14:28:55", "updateTime": None, "id": 19778, "brandId": 402, "brandName": "柳丝木", "accountId": "486887", "date": None, "unitId": None, "unitName": "信商销-小橘-隔离-成单-美妆-0824", "projectName": None, "deliveryWay": None, "product": None, "kolNote": None, "orientation": None, "deliveryWay2": None, "targetPattern": None, "status": 0}, {"createTime": "2023-08-30 14:28:55", "updateTime": None, "id": 19787, "brandId": 402, "brandName": "柳丝木", "accountId": "486887", "date": None, "unitId": None, "unitName": "信商销-小熊哭包-卸妆油-成单-0824", "projectName": None, "deliveryWay": None, "product": None, "kolNote": None, "orientation": None, "deliveryWay2": None, "targetPattern": None, "status": 0}, {"createTime": "2023-08-30 14:28:55", "updateTime": None, "id": 19776, "brandId": 402, "brandName": "柳丝木", "accountId": "486887", "date": None, "unitId": None, "unitName": "信商销-小玉酱-卸妆油-成单-美妆-0825", "projectName": None, "deliveryWay": None, "product": None, "kolNote": None, "orientation": None, "deliveryWay2": None, "targetPattern": None, "status": 0}, {"createTime": "2023-08-30 14:43:28", "updateTime": None, "id": 23580, "brandId": 402, "brandName": "柳丝木", "accountId": "486887", "date": None, "unitId": None, "unitName": "信商销-小雅很闲-卸妆油-成单-美妆-0828", "projectName": None, "deliveryWay": None, "product": None, "kolNote": None, "orientation": None, "deliveryWay2": None, "targetPattern": None, "status": 0}, {"createTime": "2023-08-30 14:28:55", "updateTime": None, "id": 19782, "brandId": 402, "brandName": "柳丝木", "accountId": "486887", "date": None, "unitId": None, "unitName": "信商销-是33崽🦋-隔离-成单-美妆-0824", "projectName": None, "deliveryWay": None, "product": None, "kolNote": None, "orientation": None, "deliveryWay2": None, "targetPattern": None, "status": 0}, {"createTime": "2023-08-30 14:43:28", "updateTime": None, "id": 23579, "brandId": 402, "brandName": "柳丝木", "accountId": "486887", "date": None, "unitId": None, "unitName": "信商销-水煮荷包蛋-卸妆油-成单-品牌种草-0828", "projectName": None, "deliveryWay": None, "product": None, "kolNote": None, "orientation": None, "deliveryWay2": None, "targetPattern": None, "status": 0}, {"createTime": "2023-08-30 14:28:55", "updateTime": None, "id": 19777, "brandId": 402, "brandName": "柳丝木", "accountId": "486887", "date": None, "unitId": None, "unitName": "信商销-水煮荷包蛋-卸妆油-成单-美妆-0825", "projectName": None, "deliveryWay": None, "product": None, "kolNote": None, "orientation": None, "deliveryWay2": None, "targetPattern": None, "status": 0}, {"createTime": "2023-08-30 14:28:55", "updateTime": None, "id": 19769, "brandId": 402, "brandName": "柳丝木", "accountId": "486887", "date": None, "unitId": None, "unitName": "信商销-水煮荷包蛋-隔离-成单-美妆-0825", "projectName": None, "deliveryWay": None, "product": None, "kolNote": None, "orientation": None, "deliveryWay2": None, "targetPattern": None, "status": 0}, {"createTime": "2023-08-30 14:28:55", "updateTime": None, "id": 19766, "brandId": 402, "brandName": "柳丝木", "accountId": "486887", "date": None, "unitId": None, "unitName": "信商销-社恐的小酒窝-隔离-成单-美妆-0825", "projectName": None, "deliveryWay": None, "product": None, "kolNote": None, "orientation": None, "deliveryWay2": None, "targetPattern": None, "status": 0}], "total": 3535, "size": 20, "current": 1, "orders": [], "optimizeCountSql": True, "searchCount": True, "countId": None, "maxLimit": None, "pages": 177}}
    print(JsonTool.json_get_path_value(dat, '$.data.tota1l'))
