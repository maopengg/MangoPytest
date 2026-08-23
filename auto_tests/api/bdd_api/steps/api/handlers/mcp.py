"""MCP Streamable HTTP 功能场景。"""

from __future__ import annotations

import base64
import json
import time

from .base import BaseHandler


class McpHandler(BaseHandler):
    def _mcp(self, case_id: str, n: int) -> FunctionalCaseResult:
        r = self.repo
        if n == 122:
            value = r.mcp_initialize(); return self.result(case_id, "result" in value, bool(r.mcp_session_id), "protocolVersion" in value["result"])
        if n == 123:
            status, _, _ = r.mcp_rpc_with_session("invalid-session", "tools/list", {})
            return self.result(case_id, status in {400, 404})
        if n == 124:
            methods = ["tools/list", "resources/templates/list", "prompts/list"]
            replies = [r.mcp_rpc(method, {})[1] for method in methods]
            return self.result(case_id, all("result" in item for item in replies), len(replies[0]["result"]["tools"]) >= 10)
        if n == 125:
            value = r.mcp_call("echo_json_types", {"boolean": True, "integer": 7, "number": 2.5, "text": "中文", "items": [1, False], "object_value": {"ok": True}, "nullable": None})["value"]
            return self.result(case_id, value["boolean"] is True, value["object_value"] == {"ok": True}, value["nullable"] is None)
        if n == 126:
            started = time.monotonic(); value = r.mcp_call("delayed_tool", {"delay_seconds": 0.1, "value": "done"})["value"]
            return self.result(case_id, time.monotonic() - started >= 0.09, value["value"] == "done")
        if n in {127, 131}:
            name = "delayed_tool" if n == 127 else "progressive_task"; args = {"delay_seconds": 2} if n == 127 else {"steps": 100, "interval_ms": 100}
            cancelled = r.mcp_cancellation_probe(name, args)
            alive = r.mcp_call("echo_json_types", {"boolean": True, "integer": 1, "number": 1.0, "text": "alive", "items": [], "object_value": {}})
            return self.result(case_id, cancelled, not alive.get("isError"))
        if n == 128:
            value = r.mcp_call("raise_business_error", {"code": "AUTO_ERROR", "message": "AUTO failure"})
            return self.result(case_id, value.get("isError") is True)
        if n == 129:
            one = r.mcp_call("large_tool_result", {"count": 1})["value"]; maximum = r.mcp_call("large_tool_result", {"count": 10000})["value"]
            return self.result(case_id, len(one["items"]) == 1, len(maximum["items"]) == 10000)
        if n == 130:
            value = r.mcp_call("progressive_task", {"steps": 5, "interval_ms": 10})["value"]
            return self.result(case_id, value == {"status": "completed", "steps": 5})
        if n == 132:
            claim = r.mcp_call("create_expense_claim", self.factory.claim())["value"]
            status, reply, _ = r.mcp_rpc("resources/read", {"uri": f"mock://workflow/{r.run_id}/{claim['id']}"})
            return self.result(case_id, status == 200, str(claim["id"]) in json.dumps(reply, ensure_ascii=False))
        if n == 133:
            claim = r.mcp_call("create_expense_claim", self.factory.claim())["value"]
            states = [r.mcp_act_claim(claim["id"], role)["status"] for role in ("dept_manager", "finance_manager", "ceo")]
            return self.result(case_id, states == ["finance_pending", "ceo_pending", "approved"])
        if n in {134, 135}:
            review = r.mcp_call("start_contract_review", self.factory.review(3 if n == 135 else 1))["value"]
            if n == 135:
                cancelled = r.mcp_call("cancel_contract_review", {"job_id": review["id"]})["value"]
                return self.result(case_id, cancelled["status"] == "cancelled")
            current = r.mcp_call("get_contract_review", {"job_id": review["id"]})["value"]
            return self.result(case_id, current["id"] == review["id"], current["progress"] >= review["progress"])
        if n == 136:
            values = []
            for size in (1, 65536):
                _, reply, _ = r.mcp_rpc("resources/read", {"uri": f"mock://binary/{size}"})
                content = reply["result"]["contents"][0]
                values.append(len(base64.b64decode(content["blob"])) == size and content["mimeType"] == "application/octet-stream")
            return self.result(case_id, *values)
        if n == 137:
            _, reply, _ = r.mcp_rpc("prompts/get", {"name": "approval_summary", "arguments": {"claim_id": "7", "status": "approved"}})
            return self.result(case_id, "7" in json.dumps(reply, ensure_ascii=False), "approved" in json.dumps(reply, ensure_ascii=False))
        if n == 138:
            requests = [
                {"jsonrpc": "2.0", "id": 301, "method": "tools/call", "params": {"name": "versioned_contract", "arguments": {"version": 1}}},
                {"jsonrpc": "2.0", "id": 302, "method": "tools/call", "params": {"name": "raise_business_error", "arguments": {}}},
                {"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 999}},
            ]
            status, reply = r.mcp_batch(requests)
            ids = (
                {item["id"] for item in reply if isinstance(item, dict) and "id" in item}
                if isinstance(reply, list)
                else set()
            )
            return self.result(case_id, status == 200, ids == {301, 302})
        value = r.mcp_call("cleanup_test_run", {"test_run_id": r.run_id})
        return self.result(case_id, value.get("isError") is True, r.request("GET", "/api/v1/auth/me").status_code == 200)
