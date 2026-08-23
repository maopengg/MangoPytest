"""HTTP Lab 功能场景。"""

from __future__ import annotations

import csv
import io
import json
import time

import httpx

from .base import BaseHandler


class HttpLabHandler(BaseHandler):
    def _http_lab(self, case_id: str, n: int) -> FunctionalCaseResult:
        r = self.repo
        if n == 48:
            methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
            responses = [r.request(method, "/api/v1/lab/methods/7", json={"method": method} if method != "GET" else None) for method in methods]
            return self.result(case_id, all(r.data(value)["method"] == method for value, method in zip(responses, methods)))
        if n == 49:
            response = r.request("GET", "/api/v1/lab/query", params=[("tag", "a"), ("tag", "b"), ("keyword", "中文")])
            data = r.data(response)
            return self.result(case_id, data["grouped"]["tag"] == ["a", "b"], data["grouped"]["keyword"] == ["中文"])
        if n == 50:
            response = r.request("GET", "/api/v1/lab/headers", headers={"X-Custom-Header": "Mango"})
            return self.result(case_id, r.data(response)["grouped_headers"]["x-custom-header"] == ["Mango"])
        if n == 51:
            payload = self.factory.json_matrix(); response = r.request("POST", "/api/v1/lab/json", json=payload)
            return self.result(case_id, r.data(response)["value"] == payload)
        if n == 52:
            response = r.request("POST", "/api/v1/lab/form", content="name=mango&tag=a&tag=b", headers={"Content-Type": "application/x-www-form-urlencoded"})
            return self.result(case_id, ["tag", "a"] in r.data(response)["items"], ["tag", "b"] in r.data(response)["items"])
        if n in {53, 54, 55}:
            body = "第一行\n第二行".encode() if n == 53 else (b"\x00\xff" if n == 54 else b"")
            response = r.request("POST", "/api/v1/lab/raw", content=body, headers={"Content-Type": "application/octet-stream" if n == 54 else "text/plain"})
            data = r.data(response)
            return self.result(case_id, response.status_code == 200, data["size"] == len(body))
        if n in {56, 57}:
            content = b"x" * (10 * 1024 * 1024 + 1) if n == 57 else b"\x00\xffbinary"
            response = r.request("POST", "/api/v1/lab/multipart", data={"description": "AUTO", "tags": ["api"]}, files=[("files", ("测试.bin", content, "application/octet-stream"))])
            if n == 57: return self.result(case_id, response.status_code == 413)
            item = r.data(response)["files"][0]
            return self.result(case_id, response.status_code == 200, item["filename"] == "测试.bin", item["size"] == len(content))
        if n == 58:
            values = {"true": True, "number": 42.5, "string": "mango", "null": None}
            return self.result(case_id, all(r.request("GET", f"/api/v1/lab/scalar/{kind}").json() == value for kind, value in values.items()))
        if n == 59:
            data = r.data(r.request("GET", "/api/v1/lab/types"))
            value_types = {type(value).__name__ for value in data.values()}
            return self.result(
                case_id,
                {"int", "str", "NoneType", "dict", "list"}.issubset(value_types),
                "中文" in data["unicode"],
            )
        if n == 60:
            response = r.request("POST", "/api/v1/lab/json", content='{"ok":true}', headers={"Content-Type": "text/plain"})
            return self.result(case_id, response.status_code == 200, r.data(response)["value"] == {"ok": True})
        if n == 61:
            response = r.request("POST", "/api/v1/lab/json", content="{invalid", headers={"Content-Type": "application/json"})
            return self.result(case_id, response.status_code == 400, response.json()["code"] == "INVALID_JSON")
        if n == 62:
            codes = [201, 400, 418, 503]
            return self.result(case_id, all(r.request("GET", f"/api/v1/lab/status/{code}").status_code == code for code in codes))
        if n == 63:
            started = time.monotonic(); response = r.request("GET", "/api/v1/lab/delay", params={"seconds": 0.3}); elapsed = time.monotonic() - started
            return self.result(case_id, response.status_code == 200, elapsed >= 0.28)
        if n == 64:
            timed_out = False
            try: r.request("GET", "/api/v1/lab/delay", params={"seconds": 3}, timeout=1)
            except httpx.TimeoutException: timed_out = True
            alive = r.request("GET", "/api/v1/lab/types")
            return self.result(case_id, timed_out, alive.status_code == 200)
        if n in {65, 66}:
            response = r.request("GET", "/api/v1/lab/redirect", params={"target": "/api/v1/lab/types"}, follow_redirects=n == 66)
            return self.result(case_id, response.status_code == (200 if n == 66 else 302), (str(response.url).endswith("/api/v1/lab/types") if n == 66 else response.headers["location"] == "/api/v1/lab/types"))
        if n == 67:
            set_result = r.request("POST", "/api/v1/lab/cookies", params={"value": "mango"}); get_result = r.request("GET", "/api/v1/lab/cookies")
            return self.result(case_id, "mango_session" in set_result.headers.get("set-cookie", ""), r.data(get_result)["cookies"]["mango_session"] == "mango")
        if n == 68:
            response = r.request("GET", "/api/v1/lab/empty")
            return self.result(case_id, response.status_code == 204, response.content == b"")
        if n == 69:
            response = r.request("GET", "/api/v1/lab/invalid-json"); failed = False
            try: response.json()
            except json.JSONDecodeError: failed = True
            return self.result(case_id, response.status_code == 200, failed)
        if n == 70:
            one = r.request("GET", "/api/v1/lab/large", params={"count": 1}); maximum = r.request("GET", "/api/v1/lab/large", params={"count": 10000})
            return self.result(case_id, r.data(one)["count"] == 1, len(r.data(maximum)["items"]) == 10000)
        if n == 71:
            response = r.request("GET", "/api/v1/lab/stream", params={"chunks": 5, "interval_ms": 0})
            return self.result(case_id, response.text.splitlines() == [f"chunk-{i}" for i in range(1, 6)])
        if n == 72:
            response = r.request("GET", "/api/v1/lab/download.csv")
            rows = list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))
            return self.result(case_id, response.status_code == 200, rows[0] == ["id", "name", "status"], rows[1][1] == "合同审查")
        if n in {73, 74}:
            first = r.request("GET", "/api/v1/lab/cache/7", params={"version": 1}); etag = first.headers["etag"]
            if n == 73:
                cached = r.request("GET", "/api/v1/lab/cache/7", params={"version": 1}, headers={"If-None-Match": etag})
                return self.result(case_id, cached.status_code == 304, cached.content == b"")
            changed = r.request("GET", "/api/v1/lab/cache/7", params={"version": 2}, headers={"If-None-Match": etag})
            return self.result(case_id, changed.status_code == 200, changed.headers["etag"] != etag)
        if n == 75:
            response = r.request("GET", "/api/v1/lab/gzip", params={"size": 5})
            return self.result(case_id, response.status_code == 200, response.headers.get("content-encoding") == "gzip", response.json()["count"] == 5)
        if n in {76, 77}:
            header = "bytes=0-9" if n == 76 else "bytes=999999-"
            response = r.request("GET", "/api/v1/lab/range", headers={"Range": header})
            return self.result(case_id, response.status_code == (206 if n == 76 else 416), len(response.content) == (10 if n == 76 else 0))
        if n == 78:
            response = r.request("GET", "/api/v1/lab/rate-limit", params={"retry_after": 1})
            return self.result(case_id, response.status_code == 429, response.headers["retry-after"] == "1")
        uploaded = r.request("POST", "/api/v1/lab/multipart", data={"description": "lifecycle"}, files={"files": ("sample.txt", b"file-content", "text/plain")})
        item = r.data(uploaded)["files"][0]; path = f"/api/v1/lab/files/{item['file_key']}"
        metadata = r.request("GET", path); downloaded = r.request("GET", path, params={"download": "true"}); deleted = r.request("DELETE", path); missing = r.request("GET", path)
        return self.result(case_id, r.data(metadata)["size"] == 12, downloaded.content == b"file-content", deleted.status_code == 200, missing.status_code == 404)
