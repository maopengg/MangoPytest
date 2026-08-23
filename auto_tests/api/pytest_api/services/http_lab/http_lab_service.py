"""HTTP 协议能力实验室 Service。"""

import csv
import io
import json
import time

import httpx

from auto_tests.api.pytest_api.services.common import ScenarioResult


class HttpLabService:
    def __init__(self, repository, factory):
        self.repository = repository
        self.factory = factory

    def echo_all_methods(self):
        methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
        responses = [self.repository.request(method, "/api/v1/lab/methods/7", json={"method": method} if method != "GET" else None) for method in methods]
        return self._result(methods_echoed=all(self.repository.data(response)["method"] == method for response, method in zip(responses, methods)))

    def echo_multivalue_query(self):
        data = self.repository.data(self.repository.request("GET", "/api/v1/lab/query", params=[("tag", "a"), ("tag", "b"), ("keyword", "中文")]))
        return self._result(tags_preserved=data["grouped"]["tag"] == ["a", "b"], unicode_preserved=data["grouped"]["keyword"] == ["中文"])

    def echo_custom_headers(self):
        data = self.repository.data(self.repository.request("GET", "/api/v1/lab/headers", headers={"X-Custom-Header": "Mango"}))
        return self._result(custom_header=data["grouped_headers"]["x-custom-header"] == ["Mango"])

    def echo_json_matrix(self):
        payload = self.factory.json_matrix()
        response = self.repository.request("POST", "/api/v1/lab/json", json=payload)
        return self._result(json_preserved=self.repository.data(response)["value"] == payload)

    def submit_urlencoded_form(self):
        response = self.repository.request("POST", "/api/v1/lab/form", content="name=mango&tag=a&tag=b", headers={"Content-Type": "application/x-www-form-urlencoded"})
        items = self.repository.data(response)["items"]
        return self._result(first_tag=["tag", "a"] in items, second_tag=["tag", "b"] in items)

    def submit_text_body(self): return self._raw("第一行\n第二行".encode(), "text/plain")
    def submit_binary_body(self): return self._raw(b"\x00\xff", "application/octet-stream")
    def submit_empty_body(self): return self._raw(b"", "text/plain")

    def upload_binary_file(self):
        content = b"\x00\xffbinary"
        response = self._multipart(content)
        item = self.repository.data(response)["files"][0]
        return self._result(success=response.status_code == 200, filename=item["filename"] == "测试.bin", size=item["size"] == len(content))

    def reject_oversized_file(self):
        return self._result(payload_too_large=self._multipart(b"x" * (10 * 1024 * 1024 + 1)).status_code == 413)

    def return_json_scalars(self):
        values = {"true": True, "number": 42.5, "string": "mango", "null": None}
        return self._result(scalars_match=all(self.repository.request("GET", f"/api/v1/lab/scalar/{kind}").json() == value for kind, value in values.items()))

    def show_json_types(self):
        data = self.repository.data(self.repository.request("GET", "/api/v1/lab/types"))
        types = {type(value).__name__ for value in data.values()}
        return self._result(types_complete={"int", "str", "NoneType", "dict", "list"}.issubset(types), unicode_present="中文" in data["unicode"])

    def accept_json_with_text_content_type(self):
        response = self.repository.request("POST", "/api/v1/lab/json", content='{"ok":true}', headers={"Content-Type": "text/plain"})
        return self._result(success=response.status_code == 200, parsed=self.repository.data(response)["value"] == {"ok": True})

    def reject_invalid_json(self):
        response = self.repository.request("POST", "/api/v1/lab/json", content="{invalid", headers={"Content-Type": "application/json"})
        return self._result(bad_request=response.status_code == 400, business_code=response.json()["code"] == "INVALID_JSON")

    def return_custom_status_codes(self):
        codes = [201, 400, 418, 503]
        return self._result(all_statuses=all(self.repository.request("GET", f"/api/v1/lab/status/{code}").status_code == code for code in codes))

    def honor_short_delay(self):
        started = time.monotonic(); response = self.repository.request("GET", "/api/v1/lab/delay", params={"seconds": 0.3})
        return self._result(success=response.status_code == 200, delayed=time.monotonic() - started >= 0.28)

    def timeout_and_recover(self):
        timed_out = False
        try:
            self.repository.request("GET", "/api/v1/lab/delay", params={"seconds": 3}, timeout=1)
        except httpx.TimeoutException:
            timed_out = True
        alive = self.repository.request("GET", "/api/v1/lab/types")
        return self._result(timed_out=timed_out, client_reusable=alive.status_code == 200)

    def redirect_without_follow(self): return self._redirect(False)
    def redirect_with_follow(self): return self._redirect(True)

    def persist_cookie(self):
        set_result = self.repository.request("POST", "/api/v1/lab/cookies", params={"value": "mango"})
        get_result = self.repository.request("GET", "/api/v1/lab/cookies")
        return self._result(cookie_set="mango_session" in set_result.headers.get("set-cookie", ""), cookie_sent=self.repository.data(get_result)["cookies"]["mango_session"] == "mango")

    def return_empty_response(self):
        response = self.repository.request("GET", "/api/v1/lab/empty")
        return self._result(no_content=response.status_code == 204, empty=response.content == b"")

    def detect_invalid_json_response(self):
        response = self.repository.request("GET", "/api/v1/lab/invalid-json")
        invalid = False
        try: response.json()
        except json.JSONDecodeError: invalid = True
        return self._result(success=response.status_code == 200, parse_failed=invalid)

    def handle_large_responses(self):
        one = self.repository.request("GET", "/api/v1/lab/large", params={"count": 1})
        maximum = self.repository.request("GET", "/api/v1/lab/large", params={"count": 10000})
        return self._result(minimum=self.repository.data(one)["count"] == 1, maximum=len(self.repository.data(maximum)["items"]) == 10000)

    def read_chunked_stream(self):
        response = self.repository.request("GET", "/api/v1/lab/stream", params={"chunks": 5, "interval_ms": 0})
        return self._result(chunks=response.text.splitlines() == [f"chunk-{index}" for index in range(1, 6)])

    def parse_csv_download(self):
        response = self.repository.request("GET", "/api/v1/lab/download.csv")
        rows = list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))
        return self._result(success=response.status_code == 200, header=rows[0] == ["id", "name", "status"], unicode=rows[1][1] == "合同审查")

    def use_matching_etag(self): return self._etag(False)
    def invalidate_changed_etag(self): return self._etag(True)

    def decode_gzip_response(self):
        response = self.repository.request("GET", "/api/v1/lab/gzip", params={"size": 5})
        return self._result(success=response.status_code == 200, gzip=response.headers.get("content-encoding") == "gzip", decoded=response.json()["count"] == 5)

    def read_valid_range(self): return self._range("bytes=0-9", 206, 10)
    def reject_invalid_range(self): return self._range("bytes=999999-", 416, 0)

    def expose_rate_limit_headers(self):
        response = self.repository.request("GET", "/api/v1/lab/rate-limit", params={"retry_after": 1})
        return self._result(rate_limited=response.status_code == 429, retry_after=response.headers["retry-after"] == "1")

    def complete_file_lifecycle(self):
        uploaded = self.repository.request("POST", "/api/v1/lab/multipart", data={"description": "lifecycle"}, files={"files": ("sample.txt", b"file-content", "text/plain")})
        item = self.repository.data(uploaded)["files"][0]; path = f"/api/v1/lab/files/{item['file_key']}"
        metadata = self.repository.request("GET", path); downloaded = self.repository.request("GET", path, params={"download": "true"})
        deleted = self.repository.request("DELETE", path); missing = self.repository.request("GET", path)
        return self._result(metadata=self.repository.data(metadata)["size"] == 12, downloaded=downloaded.content == b"file-content", deleted=deleted.status_code == 200, missing=missing.status_code == 404)

    def _raw(self, body, content_type):
        response = self.repository.request("POST", "/api/v1/lab/raw", content=body, headers={"Content-Type": content_type})
        return self._result(success=response.status_code == 200, size=self.repository.data(response)["size"] == len(body))

    def _multipart(self, content):
        return self.repository.request("POST", "/api/v1/lab/multipart", data={"description": "AUTO", "tags": ["api"]}, files=[("files", ("测试.bin", content, "application/octet-stream"))])

    def _redirect(self, follow):
        response = self.repository.request("GET", "/api/v1/lab/redirect", params={"target": "/api/v1/lab/types"}, follow_redirects=follow)
        target = str(response.url).endswith("/api/v1/lab/types") if follow else response.headers["location"] == "/api/v1/lab/types"
        return self._result(status=response.status_code == (200 if follow else 302), target=target)

    def _etag(self, changed):
        first = self.repository.request("GET", "/api/v1/lab/cache/7", params={"version": 1}); etag = first.headers["etag"]
        response = self.repository.request("GET", "/api/v1/lab/cache/7", params={"version": 2 if changed else 1}, headers={"If-None-Match": etag})
        return self._result(status=response.status_code == (200 if changed else 304), etag=(response.headers["etag"] != etag if changed else response.content == b""))

    def _range(self, header, status, size):
        response = self.repository.request("GET", "/api/v1/lab/range", headers={"Range": header})
        return self._result(status=response.status_code == status, size=len(response.content) == size)

    @staticmethod
    def _result(**checks): return ScenarioResult(checks)
