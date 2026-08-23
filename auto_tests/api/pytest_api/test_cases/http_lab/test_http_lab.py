"""HTTP Lab 纯 pytest 协议用例。"""
import allure
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.http, allure.epic("Mango Mock API 自动化"), allure.feature("HTTP Lab")]

CASES = [
    ("FTAPI-0048 分别使用 GET、POST、PUT、PATCH 和 DELETE 请求方法回显接口", "echo_all_methods"),
    ("FTAPI-0049 提交同名多值查询参数和 Unicode 查询值", "echo_multivalue_query"),
    ("FTAPI-0050 提交大小写不同及自定义请求头", "echo_custom_headers"),
    ("FTAPI-0051 提交包含对象、数组、布尔值、空值和 Unicode 的 JSON", "echo_json_matrix"),
    ("FTAPI-0052 提交 application/x-www-form-urlencoded 表单", "submit_urlencoded_form"),
    ("FTAPI-0053 提交 text/plain 原始文本请求体", "submit_text_body"),
    ("FTAPI-0054 提交 application/octet-stream 二进制请求体", "submit_binary_body"),
    ("FTAPI-0055 提交空请求体到原始请求体接口", "submit_empty_body"),
    ("FTAPI-0056 提交 multipart 表单并同时上传文本和二进制文件", "upload_binary_file"),
    ("FTAPI-0057 提交超出允许大小的 multipart 文件", "reject_oversized_file"),
    ("FTAPI-0058 请求 JSON 标量值 true、数字、字符串和 null", "return_json_scalars"),
    ("FTAPI-0059 请求类型展示接口", "show_json_types"),
    ("FTAPI-0060 发送包含错误 Content-Type 的 JSON 文本", "accept_json_with_text_content_type"),
    ("FTAPI-0061 发送语法不合法的 JSON 请求体", "reject_invalid_json"),
    ("FTAPI-0062 请求自定义 201、400、418 和 503 状态码", "return_custom_status_codes"),
    ("FTAPI-0063 请求零延迟和短延迟响应", "honor_short_delay"),
    ("FTAPI-0064 请求超过客户端超时阈值的延迟响应", "timeout_and_recover"),
    ("FTAPI-0065 请求单跳重定向且禁止客户端自动跟随", "redirect_without_follow"),
    ("FTAPI-0066 请求重定向并允许客户端自动跟随", "redirect_with_follow"),
    ("FTAPI-0067 设置 Cookie 后在后续请求中读取 Cookie", "persist_cookie"),
    ("FTAPI-0068 请求 204 空响应", "return_empty_response"),
    ("FTAPI-0069 请求声明 JSON 但返回非法 JSON 的响应", "detect_invalid_json_response"),
    ("FTAPI-0070 请求大响应体的最小值和最大值", "handle_large_responses"),
    ("FTAPI-0071 分块读取流式下载响应", "read_chunked_stream"),
    ("FTAPI-0072 下载 CSV 并解析包含逗号、引号和 Unicode 的字段", "parse_csv_download"),
    ("FTAPI-0073 携带匹配 ETag 请求缓存资源", "use_matching_etag"),
    ("FTAPI-0074 更新缓存资源后携带旧 ETag 再次请求", "invalidate_changed_etag"),
    ("FTAPI-0075 请求 gzip 压缩响应并解压", "decode_gzip_response"),
    ("FTAPI-0076 请求合法单段字节范围", "read_valid_range"),
    ("FTAPI-0077 请求超出资源长度的字节范围", "reject_invalid_range"),
    ("FTAPI-0078 连续请求直至触发限流再等待恢复", "expose_rate_limit_headers"),
    ("FTAPI-0079 上传文件后执行元数据查询、下载和删除", "complete_file_lifecycle"),
]

@pytest.mark.parametrize(("title", "method_name"), CASES, ids=[title.split()[0] for title, _ in CASES])
def test_http_lab_case(title, method_name, http_lab_service, assert_scenario):
    allure.dynamic.title(title)
    assert_scenario(getattr(http_lab_service, method_name)())
