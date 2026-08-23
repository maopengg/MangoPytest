"""gRPC 功能场景。"""

from __future__ import annotations

from .base import BaseHandler


class GrpcHandler(BaseHandler):
    def _grpc(self, case_id: str, n: int) -> FunctionalCaseResult:
        r = self.repo
        if n == 140:
            value = r.grpc_echo(text="hello", integer=7, number=2.5, boolean=True, items=["a"], attributes={"source": "bdd"})
            return self.result(case_id, value.value.text == "hello", value.value.attributes["source"] == "bdd")
        if n == 141:
            replies = [r.grpc_echo(text=text).value.text for text in ("", "中文", "🍋")]
            return self.result(case_id, replies == ["", "中文", "🍋"])
        if n in {142, 143}:
            code = r.grpc_incomplete_metadata_code(missing_run=n == 142)
            return self.result(case_id, code in {"INVALID_ARGUMENT", "UNAUTHENTICATED", "NOT_FOUND"})
        if n == 144:
            values = list(r.grpc_server_stream(3))
            return self.result(case_id, [item.index for item in values] == [1, 2, 3])
        if n == 145:
            call = r.grpc_server_stream(100, 50); first = next(call)
            return self.result(case_id, first.index == 1, call.cancel())
        if n in {146, 147}:
            values = [] if n == 147 else ["one", "two"]
            reply = r.grpc_client_stream(values)
            return self.result(case_id, reply.count == len(values), list(reply.values) == values)
        if n in {148, 149}:
            count = 3 if n == 148 else 100
            replies = list(r.grpc_chat(count))
            return self.result(case_id, len(replies) == count, [item.sequence for item in replies] == list(range(1, count + 1)))
        if n == 150:
            code, details = r.grpc_fail_result("INVALID_ARGUMENT", "AUTO")
            return self.result(case_id, code == "INVALID_ARGUMENT", "AUTO" in details)
        if n in {151, 152}:
            if n == 151:
                code, value = r.grpc_delay_result(0.05, "done", 1)
                return self.result(case_id, code == "OK", value == "done")
            code, _ = r.grpc_delay_result(1, "late", 0.05)
            alive = r.grpc_echo(text="alive")
            return self.result(case_id, code == "DEADLINE_EXCEEDED", alive.value.text == "alive")
        if n == 153:
            one = r.grpc_versioned_contract(1); two = r.grpc_versioned_contract(2)
            return self.result(case_id, "contract_id" in one, "id" in two, isinstance(one["amount"], str), isinstance(two["amount"], float))
        if n == 154:
            states = r.grpc_approve_claim(12000, "AUTO_GRPC")
            return self.result(case_id, states == ["finance_pending", "ceo_pending", "approved"])
        if n in {155, 156}:
            review = r.grpc_start_review(self.factory.unique("AUTO_CONTRACT"), 1, 2)
            if n == 155:
                current = r.grpc_get_review(review.job_id)
                return self.result(case_id, current.job_id == review.job_id, current.progress >= review.progress)
            events = list(r.grpc_watch_review(review.job_id))
            return self.result(case_id, bool(events), [item.progress for item in events] == sorted(item.progress for item in events), events[-1].status == "completed")
        health, names = r.grpc_health_and_services()
        return self.result(case_id, health == "SERVING", "mango.mock.v1.TestLabService" in names)
