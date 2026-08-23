"""Test Run、认证及核心业务功能场景。"""

from __future__ import annotations

import time
import uuid

from .base import BaseHandler


class BusinessHandler(BaseHandler):
    def _business(self, case_id: str, n: int) -> FunctionalCaseResult:
        r = self.repo
        if n == 1:
            run_id, status = self._new_run()
            return self.result(case_id, status == "201", bool(run_id))
        if n == 2:
            a, _ = self._new_run(); b, _ = self._new_run()
            ta = self._login(a).json()["data"]["access_token"]
            tb = self._login(b).json()["data"]["access_token"]
            payload = self.factory.product(sku=self.factory.unique("AUTO_SHARED"))
            pa = r.request("POST", "/api/v1/products", run_id=a, token=ta, json=payload)
            cross = r.request("GET", "/api/v1/products", run_id=b, token=tb, params={"keyword": payload["sku"]})
            return self.result(case_id, pa.status_code == 201, r.data(cross)["total"] == 0)
        if n == 3:
            response = self._login(str(uuid.uuid4()))
            return self.result(case_id, response.status_code == 404)
        if n in {4, 5}:
            other, _ = self._new_run()
            token = self._login(other).json()["data"]["access_token"]
            created = r.request("POST", "/api/v1/products", run_id=other, token=token, json=self.factory.product())
            first = self._delete_run(other)
            unavailable = self._login(other)
            if n == 4:
                return self.result(case_id, created.status_code == 201, first.status_code == 200, unavailable.status_code == 404)
            second = self._delete_run(other)
            alive = r.request("GET", "/api/v1/auth/me")
            return self.result(case_id, first.status_code == 200, second.status_code == 404, alive.status_code == 200)
        if n == 6:
            response = self._login(r.run_id)
            return self.result(case_id, response.status_code == 200, bool(r.data(response)["access_token"]))
        if n in {7, 8}:
            response = self._login(r.run_id, "employee" if n == 7 else "not_exists", "wrong")
            return self.result(case_id, response.status_code == 401, "password" not in response.text.lower())
        if n == 9:
            return self.result(case_id, r.request("GET", "/api/v1/auth/me", role=None).status_code == 401)
        if n == 10:
            return self.result(case_id, r.request("GET", "/api/v1/auth/me", role=None, token="invalid").status_code == 401)
        if n == 11:
            response = r.request("GET", "/api/v1/auth/me")
            return self.result(case_id, response.status_code == 200, r.data(response)["username"] == "employee")
        if n in {12, 13}:
            old = r.current_token("employee")
            refreshed = r.request("POST", "/api/v1/auth/refresh", token=old, role=None)
            new = r.data(refreshed)["access_token"]
            old_result = r.request("GET", "/api/v1/auth/me", token=old, role=None)
            if n == 12:
                new_result = r.request("GET", "/api/v1/auth/me", token=new, role=None)
                return self.result(case_id, refreshed.status_code == 200, old_result.status_code == 401, new_result.status_code == 200)
            repeated = r.request("POST", "/api/v1/auth/refresh", token=old, role=None)
            return self.result(case_id, refreshed.status_code == 200, repeated.status_code == 401)
        if n == 14:
            token = r.current_token("employee")
            logout = r.request("POST", "/api/v1/auth/logout", token=token, role=None)
            after = r.request("GET", "/api/v1/auth/me", token=token, role=None)
            return self.result(case_id, logout.status_code == 200, after.status_code == 401)
        if 15 <= n <= 22:
            raise KeyError(f"{case_id} 已迁移到商品域真实 BDD Steps")
        if n == 23:
            product = self._product(price=12.5); key = self.factory.unique("AUTO_ORDER")
            response = r.create_order(self.factory.order(product["id"], 2), key)
            return self.result(case_id, response.status_code == 201, float(r.data(response)["total_amount"]) == 25.0)
        if n in {24, 25}:
            product = self._product(); key = self.factory.unique("AUTO_IDEMPOTENT")
            first = r.create_order(self.factory.order(product["id"], 1), key)
            second = r.create_order(self.factory.order(product["id"], 1 if n == 24 else 2), key)
            if n == 24:
                return self.result(case_id, second.status_code == 200, r.data(first)["id"] == r.data(second)["id"], r.data(second)["idempotency_replayed"] is True)
            return self.result(case_id, second.status_code == 409, second.json()["code"] == "IDEMPOTENCY_CONFLICT")
        if n in {26, 27}:
            payload = self.factory.order(999999999, 1) if n == 26 else self.factory.order(self._product()["id"], 0)
            response = r.create_order(payload, self.factory.unique("AUTO_BAD_ORDER"))
            return self.result(case_id, response.status_code in ({404} if n == 26 else {422}))
        if 28 <= n <= 31:
            order, _ = self._order(); oid = order["id"]
            if n == 28:
                response = r.request("POST", f"/api/v1/orders/{oid}/pay")
                return self.result(case_id, response.status_code == 200, r.data(response)["status"] == "paid")
            if n == 29:
                r.request("POST", f"/api/v1/orders/{oid}/pay"); response = r.request("POST", f"/api/v1/orders/{oid}/pay")
                return self.result(case_id, response.status_code == 409)
            if n == 30:
                r.request("POST", f"/api/v1/orders/{oid}/pay"); response = r.request("POST", f"/api/v1/orders/{oid}/refund")
                return self.result(case_id, response.status_code == 200, r.data(response)["status"] == "refunded")
            response = r.request("POST", f"/api/v1/orders/{oid}/refund")
            return self.result(case_id, response.status_code == 409)
        if 32 <= n <= 42:
            return self._claims(case_id, n)
        return self._reviews(case_id, n)

    def _claims(self, case_id: str, n: int) -> FunctionalCaseResult:
        r = self.repo
        claim = self._claim(500 if n == 32 else 12000); cid = claim["id"]
        if n == 32:
            return self.result(case_id, claim["status"] == "dept_pending", len(claim["tasks"]) >= 1)
        if n == 33:
            states = [r.data(r.claim_action(cid, role, "approve"))["status"] for role in ("dept_manager", "finance_manager", "ceo")]
            return self.result(case_id, states == ["finance_pending", "ceo_pending", "approved"])
        if n == 34:
            response = r.claim_action(cid, "finance_manager", "approve")
            current = r.request("GET", f"/api/v1/claims/{cid}")
            return self.result(case_id, response.status_code in {403, 409}, r.data(current)["status"] == "dept_pending")
        if n == 35:
            response = r.claim_action(cid, "employee", "approve")
            return self.result(case_id, response.status_code in {403, 409})
        if n == 36:
            rejected = r.claim_action(cid, "dept_manager", "reject")
            later = r.claim_action(cid, "finance_manager", "approve")
            return self.result(case_id, r.data(rejected)["status"] == "rejected", later.status_code in {403, 409})
        if n == 37:
            first = r.claim_action(cid, "dept_manager", "approve"); second = r.claim_action(cid, "dept_manager", "approve")
            return self.result(case_id, first.status_code == 200, second.status_code in {403, 409})
        if n == 38:
            response = r.request("POST", f"/api/v1/claims/{cid}/withdraw")
            return self.result(case_id, response.status_code == 200, r.data(response)["status"] == "withdrawn")
        if n == 39:
            for role in ("dept_manager", "finance_manager", "ceo"):
                r.claim_action(cid, role, "approve")
            response = r.request("POST", f"/api/v1/claims/{cid}/withdraw")
            return self.result(case_id, response.status_code == 409)
        if n == 40:
            response = r.request("POST", f"/api/v1/claims/{cid}/withdraw", role="dept_manager")
            current = r.request("GET", f"/api/v1/claims/{cid}")
            return self.result(case_id, response.status_code == 409, r.data(current)["status"] == "dept_pending")
        if n == 41:
            r.claim_action(cid, "dept_manager", "approve")
            response = r.request("GET", f"/api/v1/claims/{cid}")
            data = r.data(response)
            return self.result(case_id, response.status_code == 200, data["status"] == "finance_pending", data["tasks"][0]["status"] == "approved")
        other, _ = self._new_run(); other_token = self._login(other).json()["data"]["access_token"]
        response = r.request("GET", f"/api/v1/claims/{cid}", run_id=other, token=other_token)
        return self.result(case_id, response.status_code == 404)

    def _reviews(self, case_id: str, n: int) -> FunctionalCaseResult:
        r = self.repo
        if n == 43:
            response = r.create_review(self.factory.review(2))
            return self.result(case_id, response.status_code == 202, bool(r.data(response)["id"]))
        if n == 45:
            response = r.create_review({"contract_name": "", "duration_seconds": 1, "expected_risk_count": 1})
            return self.result(case_id, response.status_code == 422)
        review = self._review(1 if n in {44, 47} else 5); jid = review["id"]
        if n == 46:
            response = r.request("DELETE", f"/api/v1/reviews/{jid}")
            return self.result(case_id, response.status_code == 200, r.data(response)["status"] == "cancelled")
        progress = []
        for _ in range(12):
            response = r.request("GET", f"/api/v1/reviews/{jid}")
            data = r.data(response); progress.append(data["progress"])
            if data["status"] == "completed": break
            time.sleep(0.15)
        if n == 44:
            return self.result(case_id, progress == sorted(progress), data["status"] == "completed")
        cancelled = r.request("DELETE", f"/api/v1/reviews/{jid}")
        return self.result(case_id, data["status"] == "completed", cancelled.status_code == 409)
