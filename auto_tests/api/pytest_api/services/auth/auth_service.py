"""认证域 Service。"""

from auto_tests.api.pytest_api.services.common import ScenarioResult


class AuthService:
    def __init__(self, repository):
        self.repository = repository

    def login_valid_employee(self) -> ScenarioResult:
        response = self.repository.login(self.repository.run_id)
        return ScenarioResult({
            "success": response.status_code == 200,
            "has_access_token": bool(self.repository.data(response)["access_token"]),
        })

    def login_wrong_password(self) -> ScenarioResult:
        return self._invalid_login("employee", "wrong")

    def login_unknown_user(self) -> ScenarioResult:
        return self._invalid_login("not_exists", "wrong")

    def current_user_without_token(self) -> ScenarioResult:
        response = self.repository.request("GET", "/api/v1/auth/me", role=None)
        return ScenarioResult({"unauthorized": response.status_code == 401})

    def current_user_with_invalid_token(self) -> ScenarioResult:
        response = self.repository.request(
            "GET", "/api/v1/auth/me", role=None, token="invalid"
        )
        return ScenarioResult({"unauthorized": response.status_code == 401})

    def current_user_with_valid_token(self) -> ScenarioResult:
        response = self.repository.request("GET", "/api/v1/auth/me")
        return ScenarioResult({
            "success": response.status_code == 200,
            "employee": self.repository.data(response)["username"] == "employee",
        })

    def refresh_token(self) -> ScenarioResult:
        old = self.repository.current_token("employee")
        refreshed = self.repository.request(
            "POST", "/api/v1/auth/refresh", token=old, role=None
        )
        new = self.repository.data(refreshed)["access_token"]
        old_result = self.repository.request("GET", "/api/v1/auth/me", token=old, role=None)
        new_result = self.repository.request("GET", "/api/v1/auth/me", token=new, role=None)
        return ScenarioResult({
            "refreshed": refreshed.status_code == 200,
            "old_invalid": old_result.status_code == 401,
            "new_valid": new_result.status_code == 200,
        })

    def reject_reused_refresh_token(self) -> ScenarioResult:
        old = self.repository.current_token("employee")
        first = self.repository.request("POST", "/api/v1/auth/refresh", token=old, role=None)
        repeated = self.repository.request("POST", "/api/v1/auth/refresh", token=old, role=None)
        return ScenarioResult({"first_success": first.status_code == 200, "reuse_rejected": repeated.status_code == 401})

    def logout_revokes_token(self) -> ScenarioResult:
        token = self.repository.current_token("employee")
        logout = self.repository.request("POST", "/api/v1/auth/logout", token=token, role=None)
        after = self.repository.request("GET", "/api/v1/auth/me", token=token, role=None)
        return ScenarioResult({"logout_success": logout.status_code == 200, "token_revoked": after.status_code == 401})

    def _invalid_login(self, username: str, password: str) -> ScenarioResult:
        response = self.repository.login(self.repository.run_id, username, password)
        return ScenarioResult({
            "unauthorized": response.status_code == 401,
            "password_not_leaked": "password" not in response.text.lower(),
        })
