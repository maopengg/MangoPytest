"""MCP 协议 Service。"""
import base64
import json
import time
from auto_tests.api.pytest_api.services.common import ScenarioResult

class McpService:
    def __init__(self, repository, factory): self.repository, self.factory = repository, factory

    def initialize_session(self):
        value = self.repository.mcp_initialize()
        return ScenarioResult({"result": "result" in value, "session": bool(self.repository.mcp_session_id), "version": "protocolVersion" in value["result"]})

    def reject_invalid_session(self):
        self.repository.mcp_initialize()
        status, _, _ = self.repository.mcp_rpc_with_session("invalid-session", "tools/list", {})
        return ScenarioResult({"rejected": status in {400, 404}})

    def list_capabilities(self):
        methods = ["tools/list", "resources/templates/list", "prompts/list"]
        replies = [self.repository.mcp_rpc(method, {})[1] for method in methods]
        return ScenarioResult({"all_results": all("result" in item for item in replies), "tools_available": len(replies[0]["result"]["tools"]) >= 10})

    def echo_json_types(self):
        value = self.repository.mcp_call("echo_json_types", {"boolean": True, "integer": 7, "number": 2.5, "text": "中文", "items": [1, False], "object_value": {"ok": True}, "nullable": None})["value"]
        return ScenarioResult({"boolean": value["boolean"] is True, "object": value["object_value"] == {"ok": True}, "null": value["nullable"] is None})

    def delayed_tool(self):
        started = time.monotonic(); value = self.repository.mcp_call("delayed_tool", {"delay_seconds": 0.1, "value": "done"})["value"]
        return ScenarioResult({"delayed": time.monotonic() - started >= 0.09, "value": value["value"] == "done"})

    def cancel_delayed_tool(self): return self._cancel("delayed_tool", {"delay_seconds": 2})

    def business_error(self):
        value = self.repository.mcp_call("raise_business_error", {"code": "AUTO_ERROR", "message": "AUTO failure"})
        return ScenarioResult({"is_error": value.get("isError") is True})

    def large_tool_result(self):
        one = self.repository.mcp_call("large_tool_result", {"count": 1})["value"]
        maximum = self.repository.mcp_call("large_tool_result", {"count": 10000})["value"]
        return ScenarioResult({"minimum": len(one["items"]) == 1, "maximum": len(maximum["items"]) == 10000})

    def progressive_task(self):
        value = self.repository.mcp_call("progressive_task", {"steps": 5, "interval_ms": 10})["value"]
        return ScenarioResult({"completed": value == {"status": "completed", "steps": 5}})

    def cancel_progressive_task(self): return self._cancel("progressive_task", {"steps": 100, "interval_ms": 100})

    def create_claim_and_read_resource(self):
        claim = self.repository.mcp_call("create_expense_claim", self.factory.claim())["value"]
        status, reply, _ = self.repository.mcp_rpc("resources/read", {"uri": f"mock://workflow/{self.repository.run_id}/{claim['id']}"})
        return ScenarioResult({"success": status == 200, "claim_present": str(claim["id"]) in json.dumps(reply, ensure_ascii=False)})

    def query_contract_review(self):
        review = self.repository.mcp_call("start_contract_review", self.factory.review(1))["value"]
        current = self.repository.mcp_call("get_contract_review", {"job_id": review["id"]})["value"]
        return ScenarioResult({"same_review": current["id"] == review["id"], "progressed": current["progress"] >= review["progress"]})

    def cancel_contract_review(self):
        review = self.repository.mcp_call("start_contract_review", self.factory.review(3))["value"]
        cancelled = self.repository.mcp_call("cancel_contract_review", {"job_id": review["id"]})["value"]
        return ScenarioResult({"cancelled": cancelled["status"] == "cancelled"})

    def read_binary_resources(self):
        checks = {}
        for size in (1, 65536):
            _, reply, _ = self.repository.mcp_rpc("resources/read", {"uri": f"mock://binary/{size}"})
            content = reply["result"]["contents"][0]
            checks[f"size_{size}"] = len(base64.b64decode(content["blob"])) == size and content["mimeType"] == "application/octet-stream"
        return ScenarioResult(checks)

    def render_approval_prompt(self):
        _, reply, _ = self.repository.mcp_rpc("prompts/get", {"name": "approval_summary", "arguments": {"claim_id": "7", "status": "approved"}})
        rendered = json.dumps(reply, ensure_ascii=False)
        return ScenarioResult({"claim_id": "7" in rendered, "status": "approved" in rendered})

    def mixed_jsonrpc_batch(self):
        requests = [
            {"jsonrpc": "2.0", "id": 301, "method": "tools/call", "params": {"name": "versioned_contract", "arguments": {"version": 1}}},
            {"jsonrpc": "2.0", "id": 302, "method": "tools/call", "params": {"name": "raise_business_error", "arguments": {}}},
            {"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 999}},
        ]
        status, reply = self.repository.mcp_batch(requests)
        ids = {item["id"] for item in reply if isinstance(item, dict) and "id" in item} if isinstance(reply, list) else set()
        return ScenarioResult({"success": status == 200, "response_ids": ids == {301, 302}})

    def reject_cleanup_without_admin(self):
        value = self.repository.mcp_call("cleanup_test_run", {"test_run_id": self.repository.run_id})
        alive = self.repository.request("GET", "/api/v1/auth/me")
        return ScenarioResult({"rejected": value.get("isError") is True, "run_alive": alive.status_code == 200})

    def _cancel(self, name, arguments):
        cancelled = self.repository.mcp_cancellation_probe(name, arguments)
        alive = self.repository.mcp_call("echo_json_types", {"boolean": True, "integer": 1, "number": 1.0, "text": "alive", "items": [], "object_value": {}})
        return ScenarioResult({"cancelled": cancelled, "session_alive": not alive.get("isError")})
