# -*- coding: utf-8 -*-
# @Description:
# @Time   : 2023-08-08 11:48
# @Author : 毛鹏
import functools
import json
from typing import Union, List
from urllib.parse import urljoin

import allure
import pytest
import time
from genson import SchemaBuilder
from requests.models import Response

from enums.api_enum import MethodEnum, IsSchemaEnum
from exceptions import PytestAutoTestError
from exceptions.error_msg import ERROR_MSG_0350
from models.api_model import ApiDataModel, ResponseModel, ApiTestCaseModel, RequestModel, ApiInfoModel
from settings.settings import PRINT_EXECUTION_RESULTS, REQUEST_TIMEOUT_FAILURE_TIME
from sources import SourcesData
from tools.log import log


# decorators/case_data.py


def case_data(
        case_id: Union[int, List[int], None] = None,
        case_name: Union[str, List[str], None] = None,
        # 新增：声明需要的fixture数据
        require_fixtures: List[str] = None,  # e.g., ["org", "user", "budget"]
        auto_cleanup: bool = True
):
    """
    用例数据装饰器 - 融合Fixture支持

    Args:
        case_id: 用例ID
        case_name: 用例名称
        require_fixtures: 需要的fixture数据类型列表
        auto_cleanup: 是否自动清理fixture数据
    """
    require_fixtures = require_fixtures or []

    def decorator(func):
        log.debug(f'开始查询用例，用例ID:{case_id} 用例名称：{case_name}')

        # 查询测试数据
        if case_id:
            test_case_list = SourcesData.get_api_test_case(is_dict=False, id=case_id)
        elif case_name:
            test_case_list = SourcesData.get_api_test_case(is_dict=False, name=case_name)
        else:
            raise PytestAutoTestError(*ERROR_MSG_0350)

        @pytest.mark.flaky(reruns=3)
        @pytest.mark.parametrize("test_case", test_case_list)
        def wrapper(self, test_case, **fixture_kwargs):
            """
            wrapper 接收 fixture 注入的参数
            fixture_kwargs 包含：org_builder, user_builder, prepared_org 等
            """
            test_case_model = ApiTestCaseModel.get_obj(test_case)

            # 设置Allure报告
            allure.dynamic.feature(test_case.get('module'))
            allure.dynamic.story(test_case.get('scene'))
            allure.dynamic.title(test_case.get('name'))
            allure.attach(test_case_model.model_dump_json(), '用例数据', allure.attachment_type.JSON)

            # ========== 核心：Fixture 数据准备 ==========
            data = ApiDataModel(test_case=test_case_model)
            cleanup_ctx = CleanupContext()

            try:
                # 根据 require_fixtures 自动调用对应 builder
                for fixture_name in require_fixtures:
                    fixture_data = _prepare_fixture_data(
                        fixture_name,
                        fixture_kwargs,
                        cleanup_ctx
                    )
                    data.add_fixture_data(fixture_name, fixture_data)
                    allure.attach(
                        str(fixture_data),
                        f'Fixture数据:{fixture_name}',
                        allure.attachment_type.JSON
                    )

                data.cleanup_context = cleanup_ctx
                log.debug(f'准备开始执行API用例，数据：{data.model_dump_json()}')

                # 执行测试函数
                func(self, data=data)

                # 基础断言
                self.ass_main(data)

            except PytestAutoTestError as error:
                log.error(error.msg)
                allure.attach(error.msg, '发生已知异常', allure.attachment_type.TEXT)
                raise error

            finally:
                # 自动清理
                if auto_cleanup and cleanup_ctx.created_entities:
                    _cleanup_fixture_data(cleanup_ctx)

        return wrapper

    return decorator


def _prepare_fixture_data(fixture_name: str, fixture_kwargs: dict, cleanup_ctx: CleanupContext):
    """
    根据名称准备fixture数据
    支持两种模式：
    1. 直接传入已构造的数据（prepared_org）
    2. 传入builder，现场构造（org_builder）
    """
    # 模式1：直接传入预构造数据
    prepared_key = f"prepared_{fixture_name}"
    if prepared_key in fixture_kwargs:
        return fixture_kwargs[prepared_key]

    # 模式2：通过builder现场构造
    builder_key = f"{fixture_name}_builder"
    if builder_key in fixture_kwargs:
        builder = fixture_kwargs[builder_key]
        data = builder.create()
        # 记录到清理上下文
        cleanup_ctx.track(fixture_name, data.get("id"), builder)
        return data

    raise PytestAutoTestError(f"未找到fixture: {fixture_name}，请确保在测试类中定义对应的fixture")


def _cleanup_fixture_data(cleanup_ctx: CleanupContext):
    """清理fixture数据（LIFO顺序）"""
    log.debug(f"开始清理 {len(cleanup_ctx.created_entities)} 个fixture数据")
    for entity in reversed(cleanup_ctx.created_entities):
        try:
            builder = entity.get("builder")
            if builder and hasattr(builder, 'delete'):
                builder.delete(entity["id"])
                log.debug(f"已清理 {entity['type']}: {entity['id']}")
        except Exception as e:
            log.warning(f"清理失败 {entity['type']}: {entity['id']}, 错误: {e}")


def request_data(api_info_id):
    def decorator(func):

        def wrapper(self, data: ApiDataModel) -> ApiDataModel:
            log.debug(f'开始查询接口数据，ID：{api_info_id}')
            api_info_model = ApiInfoModel.get_obj(SourcesData.get_api_info(id=api_info_id))
            log.debug(f'查询到接口的数据，接口ID：{api_info_model.model_dump_json()}')
            data.request = RequestModel(
                url=urljoin(self.base_data.test_object.host, api_info_model.url),
                method=MethodEnum.get_value(api_info_model.method),
                headers=api_info_model.headers if api_info_model.headers else self.base_data.headers,
                params=data.test_case.params,
                data=data.test_case.data,
                json=data.test_case.json if data.test_case.json is not None else api_info_model.json,
                file=data.test_case.file,
            )
            if api_info_model.is_schema == IsSchemaEnum.open and api_info_model.ass_schema and data.test_case.ass_schema is None:
                data.test_case.ass_schema = api_info_model.ass_schema
            log.debug(f'默认准备好的请求，数据：{data.request.model_dump_json()}')
            res_args = func(self, data)
            allure.attach(str(data.request.url), 'URL', allure.attachment_type.TEXT)
            allure.attach(str(data.request.method), '请求方法', allure.attachment_type.TEXT)
            allure.attach(json.dumps(data.request.headers, ensure_ascii=False), '请求头', allure.attachment_type.JSON)
            if data.request.params:
                allure.attach(json.dumps(data.request.params, ensure_ascii=False), '参数', allure.attachment_type.TEXT)
            if data.request.data:
                allure.attach(json.dumps(data.request.data, ensure_ascii=False), '表单', allure.attachment_type.JSON)
            if data.request.json:
                allure.attach(json.dumps(data.request.json, ensure_ascii=False), 'JSON', allure.attachment_type.JSON)
            if data.request.file:
                allure.attach(str(data.request.file), '文件', allure.attachment_type.JSON)
            allure.attach(str(data.response.status_code), '响应状态码', allure.attachment_type.TEXT)
            allure.attach(str(data.response.response_time * 1000), '响应时间（毫秒）', allure.attachment_type.TEXT)
            allure.attach(data.response.response_text, '响应结果', allure.attachment_type.TEXT)
            return res_args

        return wrapper

    return decorator


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
            allure.attach(schema_str, '结构化断言数据', allure.attachment_type.JSON)
        except Exception as e:
            allure.attach(f'获取结构化数据失败：{e}', '结构化断言数据', allure.attachment_type.TEXT)

        response_time = time.time() - start
        if response_time > REQUEST_TIMEOUT_FAILURE_TIME:
            log.error(
                f"\n{'=' * 100}\n"
                f"测试用例执行时间较长，请关注.\n"
                f"函数运行时间: {response_time} ms\n"
                f"测试用例相关数据: {response}\n"
                f"{'=' * 100}")
        try:
            response_dict = response.json()
        except json.JSONDecodeError as error:
            response_dict = {
                'error_msg': '您可以检查返回的值是否是json，如果不是，就不要使用response_dict',
                'error': str(error)
            }
        formatted_response = ''.join(response.text.split())
        log.debug(f'请求的结果，response：{formatted_response}')
        return ResponseModel(
            url=response.url,
            status_code=response.status_code,
            method=request_model.method,
            headers=response.headers,
            response_text=formatted_response,
            response_dict=response_dict,
            response_time=response_time,
            content=response.content
        )

    return swapper


def log_decorator(func):
    @functools.wraps(func)
    def swapper(self, data: ApiDataModel) -> ApiDataModel:
        data = func(self, data)
        log.debug(f'用例执行完成，整个响应体：{data.response.model_dump()}')
        if PRINT_EXECUTION_RESULTS:
            _log_msg = f"\n{'=' * 200}\n" \
                       f"用例标题: {data.test_case.name}\n" \
                       f"请求路径: {data.response.url}\n" \
                       f"请求方式: {data.response.method}\n" \
                       f"请 求 头:  {data.request.headers}\n"
            if data.request.params is not None:
                _log_msg += f"请求params：{data.request.params}\n"
            if data.request.data is not None:
                _log_msg += f"请求data：{data.request.data}\n"
            if data.request.json is not None:
                _log_msg += f"请求json：{data.request.json}\n"
            if data.request.file is not None:
                _log_msg += f"请求文件：{data.request.file}\n"
            _log_msg += f"Http状态码: {data.response.status_code}\n" \
                        f"接口响应时长: {data.response.response_time} ms\n" \
                        f"接口响应内容: {data.response.response_text}\n" \
                        f"{'=' * 200}"
            if data.response.status_code == 200 or data.response.status_code == 300:
                log.info(_log_msg)
            else:
                log.error(_log_msg)
        return data

    return swapper
