"""
通配符测试

测试 * ** *** 通配符功能
"""
import pytest
from core.dal import expect


class TestWildcard:
    """通配符测试"""
    
    def test_wildcard_star_matches_any_value(self):
        """* 匹配任意非 null 值"""
        expect("hello").should("*")
        expect(123).should("*")
        expect(1.5).should("*")
        expect(True).should("*")
        expect({"key": "value"}).should("*")
        expect([1, 2, 3]).should("*")
    
    def test_wildcard_star_not_matches_null(self):
        """* 不匹配 null"""
        with pytest.raises(AssertionError):
            expect(None).should("*")
    
    def test_wildcard_double_star_matches_object(self):
        """** 匹配任意对象"""
        expect({"key": "value"}).should("**")
        expect({}).should("**")
        expect({"nested": {"key": "value"}}).should("**")
    
    def test_wildcard_double_star_not_matches_non_object(self):
        """** 不匹配非对象"""
        with pytest.raises(AssertionError):
            expect("hello").should("**")
        with pytest.raises(AssertionError):
            expect(123).should("**")
        with pytest.raises(AssertionError):
            expect([1, 2, 3]).should("**")
    
    def test_wildcard_triple_star_matches_list(self):
        """*** 匹配任意列表"""
        expect([1, 2, 3]).should("***")
        expect([]).should("***")
        expect([{"key": "value"}]).should("***")
    
    def test_wildcard_triple_star_not_matches_non_list(self):
        """*** 不匹配非列表"""
        with pytest.raises(AssertionError):
            expect("hello").should("***")
        with pytest.raises(AssertionError):
            expect(123).should("***")
        with pytest.raises(AssertionError):
            expect({"key": "value"}).should("***")


class TestWildcardInObject:
    """对象中的通配符测试"""
    
    def test_wildcard_in_object_property(self):
        """对象属性使用通配符"""
        data = {"name": "张三", "value": 123}
        expect(data).should("""
            : {
                name: *
                value: *
            }
        """)
    
    def test_double_wildcard_in_object_property(self):
        """对象属性使用 ** 通配符"""
        data = {"config": {"key": "value"}}
        expect(data).should("""
            : {
                config: **
            }
        """)


class TestWildcardInList:
    """列表中的通配符测试"""
    
    def test_wildcard_in_list(self):
        """列表中使用通配符"""
        data = [1, "hello", {"key": "value"}]
        expect(data).should("[* * *]")
    
    def test_triple_wildcard_matches_list(self):
        """*** 匹配整个列表"""
        data = [1, 2, 3]
        expect(data).should("***")
