# -*- coding: utf-8 -*-
# @Description:
# @Time   : 2023-08-08 11:48
# @Author : 毛鹏

import functools
import json
import time
from typing import Callable
from urllib.parse import urljoin

import allure
from genson import SchemaBuilder
from requests.models import Response

from core.models import (
    ApiDataModel,
    ResponseModel,
    RequestModel,
    APIResponse,
)
from core.reporting.adapter import AllureAdapter
from core.settings.settings import PRINT_EXECUTION_RESULTS, REQUEST_TIMEOUT_FAILURE_TIME
from core.utils import log


class CleanupContext:
    """
    清理上下文管理器
    用于跟踪和管理测试中创建的fixture数据
    """

    def __init__(self):
        self.created_entities: list = []

    def track(self, entity_type: str, entity_id: int, builder=None):
        """
        跟踪创建的实体

        @param entity_type: 实体类型
        @param entity_id: 实体ID
        @param builder: 用于清理的builder实例
        """
        self.created_entities.append(
            {"type": entity_type, "id": entity_id, "builder": builder}
        )



def timer(func):
    @functools.wraps(func)
    def swapper(self, request_model: RequestModel) -> ResponseModel:
        start = time.time()
        response: Response = func(self, request_model)
        try:
            builder = SchemaBuilder()
            builder.add_object(response.json())
            schema = builder.to_schema()
            schema_str = json.dumps(schema, ensure_ascii=False)
            allure.attach(schema_str, "结构化断言数据", allure.attachment_type.JSON)
        except Exception as e:
            allure.attach(
                f"获取结构化数据失败：{e}",
                "结构化断言数据",
                allure.attachment_type.TEXT,
            )

        response_time = time.time() - start
        if response_time > REQUEST_TIMEOUT_FAILURE_TIME:
            log.error(
                f"\n{'=' * 100}\n"
                f"测试用例执行时间较长，请关注.\n"
                f"函数运行时间: {response_time} ms\n"
                f"测试用例相关数据: {response}\n"
                f"{'=' * 100}"
            )
        try:
            response_dict = response.json()
        except json.JSONDecodeError as error:
            response_dict = {
                "error_msg": "您可以检查返回的值是否是json，如果不是，就不要使用response_dict",
                "error": str(error),
            }
        formatted_response = "".join(response.text.split())
        log.debug(f"请求的结果，response：{formatted_response}")
        return ResponseModel(
            url=response.url,
            status_code=response.status_code,
            method=request_model.method,
            headers=response.headers,
            response_text=formatted_response,
            response_dict=response_dict,
            response_time=response_time,
            content=response.content,
        )

    return swapper


def log_decorator(func):
    @functools.wraps(func)
    def swapper(self, data: ApiDataModel) -> ApiDataModel:
        data = func(self, data)
        log.debug(f"用例执行完成，整个响应体：{data.response.model_dump()}")
        if PRINT_EXECUTION_RESULTS:
            _log_msg = (
                f"\n{'=' * 200}\n"
                f"用例标题: {data.test_case.name}\n"
                f"请求路径: {data.response.url}\n"
                f"请求方式: {data.response.method}\n"
                f"请 求 头:  {data.request.headers}\n"
            )
            if data.request.params is not None:
                _log_msg += f"请求params：{data.request.params}\n"
            if data.request.data is not None:
                _log_msg += f"请求data：{data.request.data}\n"
            if data.request.json is not None:
                _log_msg += f"请求json：{data.request.json}\n"
            if data.request.file is not None:
                _log_msg += f"请求文件：{data.request.file}\n"
            _log_msg += (
                f"Http状态码: {data.response.status_code}\n"
                f"接口响应时长: {data.response.response_time} ms\n"
                f"接口响应内容: {data.response.response_text}\n"
                f"{'=' * 200}"
            )
            if data.response.status_code == 200 or data.response.status_code == 300:
                log.info(_log_msg)
            else:
                log.error(_log_msg)
        return data

    return swapper


def api_allure_logger(func: Callable) -> Callable:
    """
    API 请求 Allure 日志装饰器

    自动记录 API 请求和响应信息到 Allure 报告

    使用示例：
        @api_allure_logger
        def test_api_call():
            response = client.get("/users")
            return response
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 执行原始函数
        response = func(*args, **kwargs)

        # 如果响应不是 APIResponse，直接返回
        if not isinstance(response, APIResponse):
            return response

        _log_msg = (
            f"\n{'=' * 100}\n"
            f"请求路径: {response.request_url}\n"
            f"请求方式: {response.request_method}\n"
            f"请 求 头: {response.request_headers}\n"
        )

        if response.request_params is not None:
            _log_msg += f"请求params: {response.request_params}\n"
        if response.request_data is not None:
            _log_msg += f"请求data: {response.request_data}\n"

        # 限制响应内容长度，只打印前1000字符
        response_content = json.dumps(response.data, ensure_ascii=False, default=str)[
            :1000
        ]

        _log_msg += (
            f"Http状态码: {response.status_code}\n"
            f"接口响应时长: {response.elapsed_ms} ms\n"
            f"接口响应内容: {response_content}\n"
            f"{'=' * 100}"
        )

        # 打印到命令行
        if response.status_code == 200 or response.status_code == 300:
            log.info(_log_msg)
        else:
            log.error(_log_msg)

        # 使用 AllureAdapter 添加各项信息
        AllureAdapter.attach_text("请求URL", str(response.request_url))
        AllureAdapter.attach_text("请求方法", str(response.request_method))
        AllureAdapter.attach_json("请求头", response.request_headers)

        # 添加请求数据（如果有）
        if response.request_params:
            AllureAdapter.attach_json("请求Params", response.request_params)
        if response.request_data:
            AllureAdapter.attach_json("请求数据", response.request_data)

        # 添加响应信息
        AllureAdapter.attach_text("HTTP状态码", str(response.status_code))
        AllureAdapter.attach_text("响应时长(ms)", str(response.elapsed_ms))

        # 附加响应内容
        AllureAdapter.attach_json(
            "响应数据",
            (
                response.data
                if isinstance(response.data, dict)
                else {"data": response.data}
            ),
        )
        AllureAdapter.attach_json("响应头", response.headers)

        return response

    return wrapper
