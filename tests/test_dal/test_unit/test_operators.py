"""
操作符单元测试

对应 Java: DAL-java/src/test/resources/features/dal/calculation/*.feature
"""
import pytest
from core.dal.core.operators import Operators, CompareResult, compare


class TestStrictEqual:
    """= 严格相等操作符测试"""
    
    def test_number_equal(self):
        result = Operators.strict_equal(1, 1)
        assert result.success is True
    
    def test_number_not_equal(self):
        result = Operators.strict_equal(1, 2)
        assert result.success is False
    
    def test_float_equal(self):
        result = Operators.strict_equal(1.5, 1.5)
        assert result.success is True
    
    def test_type_mismatch_int_float(self):
        """严格相等要求类型一致：int != float"""
        result = Operators.strict_equal(1, 1.0)
        assert result.success is False
    
    def test_type_mismatch_str_int(self):
        """严格相等要求类型一致：str != int"""
        result = Operators.strict_equal("1", 1)
        assert result.success is False
    
    def test_string_equal(self):
        result = Operators.strict_equal("hello", "hello")
        assert result.success is True
    
    def test_string_not_equal(self):
        result = Operators.strict_equal("hello", "world")
        assert result.success is False
    
    def test_null_equal(self):
        result = Operators.strict_equal(None, None)
        assert result.success is True
    
    def test_boolean_equal(self):
        result = Operators.strict_equal(True, True)
        assert result.success is True


class TestLooseMatch:
    """: 宽容匹配操作符测试"""
    
    def test_number_match(self):
        """数字类型互相兼容"""
        result = Operators.loose_match(1, 1.0)
        assert result.success is True
    
    def test_float_match(self):
        result = Operators.loose_match(1.5, 1.5)
        assert result.success is True
    
    def test_string_to_number(self):
        """字符串可以匹配数字"""
        result = Operators.loose_match("123", 123)
        assert result.success is True
    
    def test_number_to_string(self):
        """数字可以匹配字符串"""
        result = Operators.loose_match(123, "123")
        assert result.success is True
    
    def test_string_not_match(self):
        result = Operators.loose_match("hello", "world")
        assert result.success is False


class TestNotEqual:
    """!= 不等于操作符测试"""
    
    def test_not_equal_true(self):
        result = Operators.not_equal(1, 2)
        assert result.success is True
    
    def test_not_equal_false(self):
        result = Operators.not_equal(1, 1)
        assert result.success is False


class TestComparison:
    """> < >= <= 比较操作符测试"""
    
    def test_greater_than_true(self):
        result = Operators.greater_than(10, 5)
        assert result.success is True
    
    def test_greater_than_false(self):
        result = Operators.greater_than(5, 10)
        assert result.success is False
    
    def test_less_than_true(self):
        result = Operators.less_than(5, 10)
        assert result.success is True
    
    def test_less_than_false(self):
        result = Operators.less_than(10, 5)
        assert result.success is False
    
    def test_greater_equal_true(self):
        result = Operators.greater_equal(10, 10)
        assert result.success is True
    
    def test_greater_equal_false(self):
        result = Operators.greater_equal(5, 10)
        assert result.success is False
    
    def test_less_equal_true(self):
        result = Operators.less_equal(10, 10)
        assert result.success is True
    
    def test_less_equal_false(self):
        result = Operators.less_equal(10, 5)
        assert result.success is False
    
    def test_string_comparison(self):
        """字符串按字典序比较"""
        result = Operators.greater_than("b", "a")
        assert result.success is True


class TestLogical:
    """and or not 逻辑操作符测试"""
    
    def test_and_true_true(self):
        result = Operators.logical_and(True, True)
        assert result is True
    
    def test_and_true_false(self):
        result = Operators.logical_and(True, False)
        assert result is False
    
    def test_and_false_true(self):
        result = Operators.logical_and(False, True)
        assert result is False
    
    def test_and_false_false(self):
        result = Operators.logical_and(False, False)
        assert result is False
    
    def test_or_true_false(self):
        result = Operators.logical_or(True, False)
        assert result is True
    
    def test_or_false_true(self):
        result = Operators.logical_or(False, True)
        assert result is True
    
    def test_or_false_false(self):
        result = Operators.logical_or(False, False)
        assert result is False
    
    def test_not_true(self):
        result = Operators.logical_not(True)
        assert result is False
    
    def test_not_false(self):
        result = Operators.logical_not(False)
        assert result is True


class TestArithmetic:
    """算术操作符测试"""
    
    def test_add(self):
        result = Operators.add(1, 2)
        assert result == 3
    
    def test_subtract(self):
        result = Operators.subtract(5, 3)
        assert result == 2
    
    def test_multiply(self):
        result = Operators.multiply(3, 4)
        assert result == 12
    
    def test_divide(self):
        result = Operators.divide(10, 2)
        assert result == 5.0
    
    def test_positive(self):
        result = Operators.positive(5)
        assert result == 5
    
    def test_negative(self):
        result = Operators.negative(5)
        assert result == -5


class TestRegex:
    """/regex/ 正则匹配测试"""
    
    def test_regex_match_simple(self):
        result = Operators.regex_match("hello", "hel.*")
        assert result.success is True
    
    def test_regex_match_pattern(self):
        result = Operators.regex_match("ORD-001", r"ORD-\d+")
        assert result.success is True
    
    def test_regex_not_match(self):
        result = Operators.regex_match("hello", "world")
        assert result.success is False


class TestPropertyAccess:
    """属性访问测试"""
    
    def test_dict_property(self):
        obj = {"name": "张三", "age": 25}
        value = Operators.get_property(obj, "name")
        assert value == "张三"
    
    def test_dict_property_not_found(self):
        obj = {"name": "张三"}
        with pytest.raises(KeyError):
            Operators.get_property(obj, "age")
    
    def test_object_property(self):
        class Person:
            def __init__(self):
                self.name = "张三"
        
        obj = Person()
        value = Operators.get_property(obj, "name")
        assert value == "张三"


class TestIndexAccess:
    """索引访问测试"""
    
    def test_list_index(self):
        obj = [1, 2, 3]
        value = Operators.get_index(obj, 0)
        assert value == 1
    
    def test_list_index_out_of_range(self):
        obj = [1, 2, 3]
        with pytest.raises(IndexError):
            Operators.get_index(obj, 10)
    
    def test_dict_key(self):
        obj = {"name": "张三"}
        value = Operators.get_index(obj, "name")
        assert value == "张三"


class TestMetaOperations:
    """元数据操作测试"""
    
    def test_list_size(self):
        obj = [1, 2, 3]
        size = Operators.get_size(obj)
        assert size == 3
    
    def test_dict_size(self):
        obj = {"a": 1, "b": 2}
        size = Operators.get_size(obj)
        assert size == 2
    
    def test_dict_keys(self):
        obj = {"a": 1, "b": 2}
        keys = Operators.get_keys(obj)
        assert set(keys) == {"a", "b"}


class TestCompareFunction:
    """compare 便捷函数测试"""
    
    def test_compare_equal(self):
        result = compare("=", 1, 1)
        assert result.success is True
    
    def test_compare_loose(self):
        result = compare(":", 1, 1.0)
        assert result.success is True
    
    def test_compare_not_equal(self):
        result = compare("!=", 1, 2)
        assert result.success is True
    
    def test_compare_greater(self):
        result = compare(">", 10, 5)
        assert result.success is True
    
    def test_compare_unknown_operator(self):
        with pytest.raises(ValueError):
            compare("unknown", 1, 2)
