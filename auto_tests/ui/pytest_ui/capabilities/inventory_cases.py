"""本地 Excel 元素契约验证执行器。"""

from auto_tests.ui.pytest_ui.cases.models import InventoryCase


class InventoryCaseMixin:
    def verify_inventory(self, case: InventoryCase) -> None:
        self.goto()
        self.open_page(case.page_key)
        target = self.locator(case.element_id)
        count = target.count()
        assert count == 1, f"{case.element_id} 应唯一存在，实际匹配 {count} 个"
        actual_tag = target.first.evaluate("element => element.tagName.toLowerCase()")
        assert actual_tag == case.tag, (
            f"{case.element_id} 标签期望 {case.tag}，实际 {actual_tag}"
        )
        assert target.first.get_attribute("data-testid") == case.element_id

