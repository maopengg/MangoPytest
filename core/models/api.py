# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: API 相关数据模型
# @Time   : 2022-12-04 17:14
# @Author : 毛鹏
import json
import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from urllib.parse import parse_qsl

from mangotools.data_processor import DataClean
from pydantic import BaseModel, ConfigDict

from core.enums.api_enum import IsSchemaEnum
from core.exceptions import *

warnings.filterwarnings(
    "ignore",
    message='Field name "json"'
)


@dataclass
class APIResponse:
    """
    API 响应数据类
    
    统一的 API 响应封装，包含请求和响应信息
    """
    status_code: int
    data: Any
    headers: Dict[str, str]
    elapsed_ms: float
    # 存储请求信息用于 Allure 记录
    request_method: str = field(default="")
    request_url: str = field(default="")
    request_headers: Dict[str, Any] = field(default_factory=dict)
    request_params: Optional[Dict[str, Any]] = field(default=None)
    request_data: Optional[Any] = field(default=None)

    @property
    def is_success(self) -> bool:
        """是否成功响应"""
        return 200 <= self.status_code < 300

    @property
    def is_error(self) -> bool:
        """是否错误响应"""
        return not self.is_success


def json_serialize(data: str | None, field: str | None = None):
    try:
        if isinstance(data, str):
            return json.loads(data)
        else:
            return data
    except (json.decoder.JSONDecodeError, TypeError):
        if field is None:
            raise ToolsError(*ERROR_MSG_0345, value=(data,))
        if field == 'params':
            if field == 'params':
                try:
                    return dict(parse_qsl(data))
                except Exception as e2:
                    raise ToolsError(*ERROR_MSG_0345, value=(data, f"parse_qs failed: {str(e2)}")) from e2


class ApiInfoModel(BaseModel):
    id: int
    project_name: str
    name: str
    client_type: int
    method: int
    url: str
    json: dict | list | None = None
    headers: dict | None = None
    is_schema: IsSchemaEnum | None = None
    ass_schema: dict | list[dict] | list | None = None

    @classmethod
    def get_obj(cls, data: dict):
        return cls(
            id=data['id'],
            project_name=data['project_name'],
            name=data['name'],
            client_type=data['client_type'],
            method=data['method'],
            url=data['url'],
            headers=json_serialize(data.get('headers')),
            json=json_serialize(data.get('JSON')),
            is_schema=data.get('is_schema'),
            ass_schema=json_serialize(data.get('ass_schema')),
        )


class RequestModel(BaseModel):
    url: str
    method: str
    headers: dict | None = None
    params: dict | None = None
    data: str | dict | None = None
    json: dict | list | None = None
    file: list | None = None


class ResponseModel(BaseModel):
    url: str
    status_code: int
    method: str
    headers: dict
    response_text: str
    response_dict: dict | list | None = None
    response_time: int | float | None = None
    content: bytes | None = None


class ApiDataModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    data_clean: DataClean = DataClean()  # 缓存数据
    request: RequestModel | None = None
    response: ResponseModel | None = None
    other_data: dict = {}  # 其他数据
