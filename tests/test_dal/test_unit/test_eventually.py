"""
异步等待测试

测试 ::eventually 功能
"""
import pytest
import time
import threading
from core.dal import expect


class TestEventually:
    """异步等待测试"""

    def test_eventually_immediate_success(self):
        """立即成功的条件"""
        data = [1, 2, 3, 4, 5]
        expect(data).should("::eventually ::size = 5")

    def test_eventually_with_delay(self):
        """延迟后成功的条件"""
        data = []

        def add_items():
            time.sleep(0.5)
            data.extend([1, 2, 3])

        # 启动线程添加元素
        thread = threading.Thread(target=add_items)
        thread.start()

        try:
            # 等待条件成立
            expect(data).should("::eventually ::size = 3")
        finally:
            thread.join()

    def test_eventually_timeout(self):
        """超时失败"""
        data = [1, 2]

        with pytest.raises(AssertionError) as exc_info:
            expect(data).should("::eventually ::size = 5")

        assert "timeout" in str(exc_info.value).lower()

    def test_eventually_with_object(self):
        """等待对象属性"""
        data = {"status": "pending"}

        def update_status():
            time.sleep(0.3)
            data["status"] = "completed"

        thread = threading.Thread(target=update_status)
        thread.start()

        try:
            expect(data).should("::eventually status = 'completed'")
        finally:
            thread.join()

    def test_eventually_nested_property(self):
        """等待嵌套属性"""
        data = {"user": {"name": "Alice", "active": False}}

        def activate():
            time.sleep(0.3)
            data["user"]["active"] = True

        thread = threading.Thread(target=activate)
        thread.start()

        try:
            expect(data).should("::eventually user.active = True")
        finally:
            thread.join()
