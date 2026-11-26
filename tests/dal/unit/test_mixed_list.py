"""
混合列表对象测试

测试列表中包含不同类型元素的支持
"""
import pytest
from core.dal import expect


class TestMixedList:
    """混合列表测试"""

    def test_mixed_list_with_primitives(self):
        """包含基本类型的混合列表"""
        data = [1, "hello", 3.14, True, None]
        expect(data).should("[1 'hello' 3.14 true null]")

    def test_mixed_list_with_objects(self):
        """包含对象的混合列表"""
        data = [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30}
        ]
        expect(data).should("""
            [{
                name: Alice
                age: *
            } {
                name: Bob
                age: *
            }]
        """)

    def test_mixed_list_with_nested_lists(self):
        """包含嵌套列表的混合列表"""
        data = [1, [2, 3], {"key": "value"}]
        expect(data).should("[1 [2 3] {key: value}]")

    def test_mixed_list_with_wildcards(self):
        """使用通配符验证混合列表"""
        data = [1, "hello", {"key": "value"}]
        expect(data).should("[* * *]")

    def test_mixed_list_strict_mode(self):
        """严格模式下的混合列表"""
        data = [1, "hello", 3.14]
        expect(data).should("=[1 'hello' 3.14]")

    def test_mixed_list_size(self):
        """混合列表的大小"""
        data = [1, "hello", {"key": "value"}, [1, 2]]
        expect(data).should("::size = 4")


class TestMixedListWithSchema:
    """混合列表与 Schema 结合测试"""

    def test_mixed_list_with_schema_validation(self):
        """对混合列表中的对象进行 Schema 验证"""
        data = [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@test.org"}
        ]
        expect(data).should("""
            [{
                name: is String
                email: is String
            } *]
        """)
