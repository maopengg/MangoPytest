from core.execution.evidence import safe_value
from core.execution.pytest_evidence_plugin import _ui_operation_evidence


def test_safe_value_keeps_debug_values_and_bounds_binary() -> None:
    value = safe_value({
        "Authorization": "Bearer unsafe",
        "body": {"password": "unsafe", "name": "AUTO_USER"},
        "payload": b"abc",
    })
    assert value["Authorization"] == "Bearer unsafe"
    assert value["body"]["password"] == "unsafe"
    assert value["body"]["name"] == "AUTO_USER"
    assert value["payload"] == {"type": "bytes", "size": 3, "preview": "616263"}


class _FakeFirstLocator:
    def evaluate(self, expression, *, timeout):
        assert "getBoundingClientRect" in expression
        assert timeout == 500
        return {
            "tag_name": "button", "text": "提交", "value": None,
            "attributes": {"data-testid": "submit"},
            "visible": True, "enabled": True, "editable": False,
            "bounding_box": {"x": 10, "y": 20, "width": 80, "height": 32},
        }


class _FakeLocator:
    first = _FakeFirstLocator()

    def count(self):
        return 1

    def __repr__(self):
        return "<Locator data-testid=submit>"


def test_ui_operation_evidence_structures_locator_snapshot() -> None:
    evidence = _ui_operation_evidence("w_click", (_FakeLocator(),), {})

    assert evidence["arguments"] == [{"element_reference": "element-1"}]
    assert evidence["elements"][0] == {
        "reference": "element-1",
        "source": "位置参数 1",
        "locator": "<Locator data-testid=submit>",
        "match_count": 1,
        "element": {
            "tag_name": "button", "text": "提交", "value": None,
            "attributes": {"data-testid": "submit"},
            "visible": True, "enabled": True, "editable": False,
            "bounding_box": {"x": 10, "y": 20, "width": 80, "height": 32},
        },
    }
