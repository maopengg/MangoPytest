from dataclasses import dataclass
from typing import Text, Dict, Union, Optional, List

from pydantic import BaseModel


@dataclass
class TestMetrics:
    """ 用例执行数据 """
    passed: int
    failed: int
    broken: int
    skipped: int
    total: int
    pass_rate: float
    time: Text


class DependentData(BaseModel):
    dependent_type: Text
    jsonpath: Text
    set_cache: Optional[Text]
    replace_key: Optional[Text]


class DependentCaseData(BaseModel):
    case_id: Text
    # dependent_data: List[DependentData]
    dependent_data: Union[None, List[DependentData]] = None


class ParamPrepare(BaseModel):
    dependent_type: Text
    jsonpath: Text
    set_cache: Text


class SendRequest(BaseModel):
    dependent_type: Text
    jsonpath: Optional[Text]
    cache_data: Optional[Text]
    set_cache: Optional[Text]
    replace_key: Optional[Text]


class TearDown(BaseModel):
    case_id: Text
    param_prepare: Optional[List["ParamPrepare"]]
    send_request: Optional[List["SendRequest"]]


class CurrentRequestSetCache(BaseModel):
    type: Text
    jsonpath: Text
    name: Text


# class TestCase(BaseModel):
#     url: Text
#     method: Text
#     detail: Text
#     # assert_data: Union[Dict, Text] = Field(..., alias="assert")
#     assert_data: Union[Dict, Text]
#     headers: Union[None, Dict, Text] = {}
#     requestType: Text
#     is_run: Union[None, bool] = None
#     data: Union[Dict, None, Text, List] = None
#     dependence_case: Union[None, bool] = False
#     dependence_case_data: Optional[Union[None, List["DependentCaseData"], Text]] = None
#     sql: List = None
#     setup_sql: List = None
#     status_code: Optional[int] = None
#     teardown_sql: Optional[List] = None
#     teardown: Union[List["TearDown"], None] = None
#     current_request_set_cache: Optional[List["CurrentRequestSetCache"]]
#     sleep: Optional[Union[int, float]]


class ResponseData(BaseModel):
    url: Text
    is_run: Union[None, bool]
    detail: Text
    response_data: Text
    request_body: Union[None, Dict, List]
    method: Text
    sql_data: Dict
    yaml_data: "TestCase"
    headers: Dict
    cookie: Dict
    assert_data: Dict
    res_time: Union[int, float]
    status_code: int
    teardown: List["TearDown"] = None
    teardown_sql: Union[None, List]
    body: Union[Dict, None, List] = None


class DingTalk(BaseModel):
    webhook: Union[Text, None]
    secret: Union[Text, None]


class MySqlDB(BaseModel):
    switch: bool = False
    host: Union[Text, None] = None
    user: Union[Text, None] = None
    password: Union[Text, None] = None
    port: Union[int, None] = 3306


class Webhook(BaseModel):
    webhook: Union[Text, None]


class Email(BaseModel):
    send_user: Union[Text, None]
    email_host: Union[Text, None]
    stamp_key: Union[Text, None]
    # 收件人
    send_list: Union[Text, None]


class Config(BaseModel):
    project_name: Text
    env: Text
    tester_name: Text
    notification_type: int = 0
    excel_report: bool
    ding_talk: "DingTalk"
    mysql_db: "MySqlDB"
    mirror_source: Text
    wechat: "Webhook"
    email: "Email"
    lark: "Webhook"
    real_time_update_test_cases: bool = False
    host: Text
    app_host: Union[Text, None]
