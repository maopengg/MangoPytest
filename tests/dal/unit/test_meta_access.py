"""
元数据访问测试

测试 ::size, ::keys, ::type, ::root, ::this, ::common 等元数据访问
"""
import pytest
from core.dal import expect


class TestMetaSize:
    """::size 元数据测试"""
    
    def test_meta_size_dict(self):
        """字典的 ::size"""
        data = {"a": 1, "b": 2, "c": 3}
        expect(data).should("::size = 3")
    
    def test_meta_size_list(self):
        """列表的 ::size"""
        data = [1, 2, 3, 4, 5]
        expect(data).should("::size = 5")
    
    def test_meta_size_empty_dict(self):
        """空字典的 ::size"""
        expect({}).should("::size = 0")
    
    def test_meta_size_empty_list(self):
        """空列表的 ::size"""
        expect([]).should("::size = 0")
    
    def test_meta_size_string(self):
        """字符串的 ::size（长度）"""
        expect("hello").should("::size = 5")


class TestMetaType:
    """::type 元数据测试"""
    
    def test_meta_type_dict(self):
        """字典的 ::type"""
        data = {"key": "value"}
        expect(data).should("::type = dict")
    
    def test_meta_type_list(self):
        """列表的 ::type"""
        data = [1, 2, 3]
        expect(data).should("::type = list")
    
    def test_meta_type_string(self):
        """字符串的 ::type"""
        expect("hello").should("::type = str")
    
    def test_meta_type_number(self):
        """数字的 ::type"""
        expect(123).should("::type = int")
        expect(1.5).should("::type = float")


class TestMetaKeys:
    """::keys 元数据测试"""
    
    def test_meta_keys_dict(self):
        """字典的 ::keys"""
        data = {"name": "张三", "age": 25}
        result = expect(data).should("::keys")
        # 验证返回的是键列表
    
    def test_meta_keys_empty_dict(self):
        """空字典的 ::keys"""
        expect({}).should("::keys = []")


class TestMetaThis:
    """::this 元数据测试"""
    
    def test_meta_this_dict(self):
        """::this 返回当前对象"""
        data = {"name": "张三"}
        expect(data).should("::this.name = 张三")
    
    def test_meta_this_list(self):
        """::this 返回当前列表"""
        data = [1, 2, 3]
        expect(data).should("::this[0] = 1")


class TestMetaCommon:
    """::common 元数据测试"""
    
    def test_meta_common_dict(self):
        """字典的 ::common 返回所有键"""
        data = {"a": 1, "b": 2}
        expect(data).should("::common")
    
    def test_meta_common_list_of_objects(self):
        """对象列表的 ::common 返回公共键"""
        data = [
            {"name": "A", "age": 20},
            {"name": "B", "age": 25}
        ]
        expect(data).should("::common")


class TestMetaInExpression:
    """在复杂表达式中使用元数据"""
    
    def test_meta_size_in_comparison(self):
        """::size 在比较表达式中"""
        data = [1, 2, 3, 4, 5]
        expect(data).should("::size > 3")
        expect(data).should("::size >= 5")
        expect(data).should("::size < 10")
    
    def test_meta_size_in_logical(self):
        """::size 在逻辑表达式中"""
        data = [1, 2, 3]
        expect(data).should("::size > 2 and ::size < 5")
