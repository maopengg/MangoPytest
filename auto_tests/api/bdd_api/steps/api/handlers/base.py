"""L4 功能场景 Handler 基类。"""

from auto_tests.api.bdd_api.data_factory.entities.functional_case import FunctionalCaseResult
from auto_tests.api.bdd_api.data_factory.factories import FunctionalCaseFactory
from auto_tests.api.bdd_api.repos.functional_cases import FunctionalCaseRepository


class BaseHandler:
    def __init__(self, repository: FunctionalCaseRepository, factory: FunctionalCaseFactory):
        self.repo = repository
        self.factory = factory

    @staticmethod
    def result(case_id: str, *checks: bool, **details) -> FunctionalCaseResult:
        return FunctionalCaseResult(case_id=case_id, checks=list(checks), details=details)

    def execute(self, case_id: str) -> FunctionalCaseResult:
        number = int(case_id.rsplit("-", 1)[1])
        log.info(f"开始执行功能用例: {case_id}")
        if number <= 47:
            return self._business(case_id, number)
        if number <= 79:
            return self._http_lab(case_id, number)
        if number <= 95:
            return self._fault_webhook(case_id, number)
        if number <= 105:
            return self._sse(case_id, number)
        if number <= 121:
            return self._websocket(case_id, number)
        if number <= 139:
            return self._mcp(case_id, number)
        if number <= 157:
            return self._grpc(case_id, number)
        raise KeyError(f"该执行器不负责跨协议场景: {case_id}")

    def _new_run(self) -> tuple[str, str]:
        response = self.repo.create_test_run(self.factory.unique("AUTO_RUN"))
        return response.json()["data"]["id"], str(response.status_code)

    def _login(self, run_id: str, username: str = "employee", password: str = "password123"):
        return self.repo.login(run_id, username, password)

    def _delete_run(self, run_id: str):
        return self.repo.delete_test_run(run_id)

    def _product(self, **overrides) -> dict:
        response = self.repo.create_product(self.factory.product(**overrides))
        assert response.status_code == 201, response.text
        return self.repo.data(response)

    def _order(self, quantity: int = 1) -> tuple[dict, str]:
        product = self._product()
        key = self.factory.unique("AUTO_ORDER")
        response = self.repo.create_order(self.factory.order(product["id"], quantity), key)
        assert response.status_code == 201, response.text
        return self.repo.data(response), key

    def _claim(self, amount: float = 12000) -> dict:
        response = self.repo.create_claim(self.factory.claim(amount))
        assert response.status_code == 201, response.text
        return self.repo.data(response)

    def _review(self, duration: int = 2) -> dict:
        response = self.repo.create_review(self.factory.review(duration))
        assert response.status_code == 202, response.text
        return self.repo.data(response)
