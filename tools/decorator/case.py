# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-09-15 10:26
# @Author : 毛鹏
import time
from functools import wraps
from json import JSONDecodeError

from requests.models import Response

from models.api_model import ApiDataModel, ResponseDataModel, CaseGroupModel
from tools.logging_tool.log_control import ERROR, WARNING, INFO


def timer(number: int):
    """
    封装统计函数执行时间装饰器
    :param number: 函数预计运行时长
    :return:
    """

    def decorator(func):
        def swapper(*args, **kwargs) -> ApiDataModel:
            s = time.time()
            res: Response = func(*args, **kwargs)
            end = time.time() - s
            # 计算时间戳毫米级别，如果时间大于number，则打印 函数名称 和运行时间
            if end > number:
                WARNING.logger.error(
                    f"\n{'=' * 100}\n"
                    "测试用例执行时间较长，请关注.\n"
                    "函数运行时间: %s ms\n"
                    "测试用例相关数据: %s\n"
                    f"{'=' * 100}"
                    , end, res)
            data: ApiDataModel = args[1]
            data.db_is_ass = args[0].data_model.db_is_ass
            group: CaseGroupModel = data.requests_list[data.step]
            group.response_time = end
            if res.text == '' or res.text is None:
                # raise ResponseError('响应结果为空，用例失败！')
                assert False
            try:
                da = res.json()
            except JSONDecodeError:
                da = res.text
            group.response = ResponseDataModel(url=res.url,
                                               status_code=res.status_code,
                                               method=res.request.method,
                                               headers=res.headers,
                                               body=group.request.data,
                                               encoding=res.encoding,
                                               content=res.content,
                                               text=res.text,
                                               response_json=da)

            return args[1]

        return swapper

    return decorator


def log_decorator(switch: bool):
    """
    封装日志装饰器, 打印请求信息
    :param switch: 定义日志开关
    :return:
    """

    def decorator(func):
        @wraps(func)
        def swapper(*args, **kwargs) -> tuple[ApiDataModel, dict]:
            res, response_dict = func(*args, **kwargs)
            # 判断日志开关为开启状态
            group: CaseGroupModel = res.requests_list[res.step]

            if switch:
                _log_msg = f"\n{'=' * 100}\n" \
                           f"用例标题: {res.test_case_data.case_name}\n" \
                           f"请求路径: {group.request.url}\n" \
                           f"请求方式: {group.request.method}\n" \
                           f"请求头:   {group.request.headers}\n" \
                           f"请求内容: {group.request.json_data}{group.request.params}{group.request.data}\n" \
                           f"接口响应内容: {group.response.text}\n" \
                           f"接口响应时长: {group.response_time} ms\n" \
                           f"Http状态码: {group.response.status_code}\n" \
                           f"{'=' * 100}"
                if group.response.status_code == 200 or group.response.status_code == 300:
                    INFO.logger.info(_log_msg)
                else:
                    # 失败的用例，控制台打印红色
                    ERROR.logger.error(_log_msg)
            return res, response_dict

        return swapper

    return decorator
