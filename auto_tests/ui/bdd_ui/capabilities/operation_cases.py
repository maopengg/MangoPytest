"""mangoautomation 同步操作能力用例执行器。"""

import json
from pathlib import Path
from typing import Any

from playwright.sync_api import Locator

from auto_tests.ui.bdd_ui.cases.models import OperationCase
from auto_tests.ui.bdd_ui.config import settings


class OperationCaseMixin:
    def execute_operation(self, case: OperationCase) -> Any:
        self.goto()
        self.open_page("componentsPage")
        params = self._expand(case.params)
        target = self._operation_target(case)
        self._prepare_operation(case, target, params)
        result = self._invoke(case.method, target, params)
        self._complete_operation(case)
        self._verify_operation(case, target, result, params)
        return result

    def _prepare_operation(
        self, case: OperationCase, target: Locator, params: dict[str, Any]
    ) -> None:
        if case.method.startswith("w_keyboard") or case.method == "w_keys":
            self.w_focus(self.locator("keyboard-target"))
        if case.method in {"w_get_input_value", "w_keyboard_delete_text"}:
            self.w_input(self.locator("keyboard-target"), "AUTO_KEYBOARD_VALUE")
            self.w_focus(self.locator("keyboard-target"))
        if case.method == "w_mouse_wheel_xy":
            self.w_scroll_to_element(self.locator("scroll-operation-target"))
        if case.method in {
            "w_mouse_click", "w_mouse_move", "w_mouse_dblclick", "w_mouse_right_click",
        }:
            box = self.locator("coordinate-pad").bounding_box()
            assert box is not None, "coordinate-pad 不可见，无法计算鼠标坐标"
            params["x"] = round(box["x"] + box["width"] / 2)
            params["y"] = round(box["y"] + box["height"] / 2)
        if case.method in {"w_mouse_down", "w_mouse_up"}:
            box = self.locator("coordinate-pad").bounding_box()
            assert box is not None, "coordinate-pad 不可见，无法准备鼠标位置"
            self.page.mouse.move(
                box["x"] + box["width"] / 2,
                box["y"] + box["height"] / 2,
            )
        if case.method in {"w_switch_tabs", "w_close_current_tab"}:
            new_page = self.base_data.context.new_page()
            new_page.goto(f"{settings.BASE_URL}/static/iframe.html?source=bdd-prepare")
            new_page.bring_to_front()
            self.base_data.page = new_page
            if case.method == "w_switch_tabs":
                params["individual"] = 2
        if case.method in {"w_close_page_by_index", "w_switch_latest_tab"}:
            self.base_data.context.new_page()
            if case.method == "w_close_page_by_index":
                params["individual"] = 2
        if case.method == "w_go_back":
            self.w_click(self.locator("push-history-state"))
        if case.method == "w_go_forward":
            self.w_click(self.locator("push-history-state"))
            self.w_go_back()
        if case.method == "w_set_cookie":
            params["storage_state"] = json.dumps(
                params["storage_state"], ensure_ascii=False
            )
        if case.method in {"w_get_cookie", "w_clear_cookies", "w_clear_storage"}:
            self.w_click(self.locator("seed-browser-storage"))
        if case.method == "w_wait_for_timeout":
            params["_time"] = 1
        if case.method == "w_tap":
            target.scroll_into_view_if_needed()
        if case.method == "w_open_new_tab_and_switch":
            params.pop("target_element_id", None)

    def _complete_operation(self, case: OperationCase) -> None:
        if case.method in {"w_accept_dialog", "w_dismiss_dialog"}:
            self.w_click(self.locator("native-confirm"))
        elif case.method == "w_add_init_script":
            self.w_goto(settings.BASE_URL)

    def _verify_operation(
        self,
        case: OperationCase,
        target: Locator,
        result: Any,
        params: dict[str, Any],
    ) -> None:
        if case.method in {
            "w_get_text", "w_get_attribute", "w_get_input_value", "w_get_inner_html",
            "w_get_texts", "w_evaluate", "w_get_title", "w_get_url", "w_content",
        }:
            assert result not in (None, "", []), f"{case.method} 应返回有效结果"
        elif case.method in {"w_ele_screenshot", "w_screenshot"}:
            assert Path(params["path"]).is_file(), f"截图文件未生成：{params['path']}"
        elif case.method == "w_download":
            download_path = self.base_data.test_data.get_cache(params["file_key"])
            assert download_path and Path(download_path).is_file(), "下载文件未生成"
        elif case.method == "w_get_cookie":
            assert Path(self.base_data.download_path, "storage_state.json").is_file()
        elif case.method == "w_set_cookie":
            assert any(
                cookie["name"] == "ui_case"
                for cookie in self.base_data.context.cookies()
            )
        elif case.method == "w_clear_cookies":
            assert not self.base_data.context.cookies()
        elif case.method == "w_clear_storage":
            storage = self.page.evaluate(
                "() => [localStorage.getItem('mango-ui-local'), "
                "sessionStorage.getItem('mango-ui-session')]"
            )
            assert storage == [None, None]
        elif case.method == "w_add_init_script":
            assert self.page.evaluate("() => window.__mangoAutomationInit") is True
        elif case.method in {"w_input", "w_clear_input"}:
            assert target.input_value() == str(params["input_value"])
        elif case.method == "w_clear":
            assert target.input_value() == ""
        elif case.method in {"w_check", "w_set_checked"}:
            assert target.is_checked()
        elif case.method == "w_uncheck":
            assert not target.is_checked()
        elif case.method == "w_select_option":
            assert params["values"] in target.input_value()
        elif case.method in self.ASSERTION_METHODS:
            assert result is not None, f"{case.method} 未返回断言结果"
        elif case.method in {"w_accept_dialog", "w_dismiss_dialog"}:
            text = self.locator("native-dialog-result").inner_text()
            expected = "接受" if case.method == "w_accept_dialog" else "取消"
            assert expected in text
        else:
            assert target.count() >= 1 or case.method in {
                "w_close_current_tab", "w_close_page_by_index", "w_new_page",
            }

    def _operation_target(self, case: OperationCase) -> Locator:
        target = self.locator(case.target_id)
        if case.method == "w_many_click" and case.target_id == "many-click-targets":
            return target.locator("button")
        if (
            case.method in {"w_get_texts", "w_to_have_count", "w_to_element_count"}
            and case.target_id == "multiple-text-targets"
        ):
            return target.locator("span")
        return target

