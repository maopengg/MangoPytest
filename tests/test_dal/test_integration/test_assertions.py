"""
断言 API 集成测试

对应 Java: DAL-java/src/test/resources/features/dal/verification/*.feature
"""
import pytest
from core.dal import expect


class TestBasicAssertions:
    """基础断言测试"""
    
    def test_strict_equal_number(self):
        """数字严格相等"""
        expect(1).should("= 1")
        expect(1.5).should("= 1.5")
    
    def test_strict_equal_string(self):
        """字符串严格相等"""
        expect("hello").should("= 'hello'")
    
    def test_loose_match_number(self):
        """数字宽容匹配：int 匹配 float"""
        expect(1).should(": 1.0")
    
    def test_loose_match_string(self):
        """字符串宽容匹配"""
        expect("123").should(": 123")
    
    def test_not_equal(self):
        """不等于"""
        expect(1).should("!= 2")
    
    def test_comparison(self):
        """比较操作"""
        expect(10).should("> 5")
        expect(10).should("< 20")
        expect(10).should(">= 10")
        expect(10).should("<= 10")


class TestLogicalAssertions:
    """逻辑断言测试"""
    
    def test_and(self):
        """逻辑与"""
        expect(5).should("> 3 and < 10")
    
    def test_or(self):
        """逻辑或"""
        expect("active").should("= 'active' or = 'pending'")
    
    def test_not(self):
        """逻辑非"""
        expect("deleted").should("not = 'active'")
    
    def test_complex_logical(self):
        """复杂逻辑组合"""
        expect(5).should("> 3 and < 10 and not = 7")


class TestObjectAssertions:
    """对象断言测试"""
    
    def test_loose_object(self):
        """宽容对象验证：只验证指定字段"""
        user = {"name": "张三", "age": 25, "email": "test@test.com"}
        expect(user).should("""
            : {
                name: '张三'
                age: 25
            }
        """)
    
    def test_strict_object(self):
        """严格对象验证：对象不能有多余字段"""
        user = {"name": "张三", "age": 25}
        expect(user).should("""
            = {
                name: '张三'
                age: 25
            }
        """)
    
    def test_nested_object(self):
        """嵌套对象验证"""
        user = {
            "name": "张三",
            "address": {"city": "北京", "zip": "100000"}
        }
        expect(user).should("""
            : {
                address.city: '北京'
                address.zip: '100000'
            }
        """)
    
    def test_field_exists(self):
        """字段存在性检查"""
        user = {"name": "张三", "email": "test@test.com"}
        expect(user).should("""
            : {
                name?          # name 必须存在
                phone?:        # phone 可选
            }
        """)


class TestListAssertions:
    """列表断言测试"""
    
    def test_list_size(self):
        """列表大小验证"""
        orders = [{"id": 1}, {"id": 2}]
        expect(orders).should(".size = 2")
    
    def test_list_index_access(self):
        """列表索引访问"""
        orders = [{"id": 1}, {"id": 2}]
        expect(orders).should("[0].id = 1")
        expect(orders).should("[1].id = 2")
    
    def test_list_strict_match(self):
        """严格列表匹配"""
        orders = [
            {"orderId": "ORD-001", "status": "PAID"},
            {"orderId": "ORD-002", "status": "PENDING"}
        ]
        expect(orders).should("""
            = [{
                orderId: 'ORD-001'
                status: PAID
            } {
                orderId: 'ORD-002'
                status: PENDING
            }]
        """)


class TestRegexAssertions:
    """正则断言测试"""
    
    def test_regex_match(self):
        """正则匹配"""
        expect("hello world").should("= /hello.*/")
        expect("ORD-001").should("= /ORD-\d+/")


class TestTableAssertions:
    """表格断言测试"""
    
    def test_table_loose(self):
        """宽松表格验证"""
        orders = [
            {"orderId": "ORD-001", "status": "PAID"},
            {"orderId": "ORD-002", "status": "PENDING"}
        ]
        expect(orders).should("""
            : | orderId  | status   |
              | ORD-001  | PAID     |
              | ORD-002  | PENDING  |
        """)
    
    def test_table_strict(self):
        """严格表格验证"""
        orders = [
            {"orderId": "ORD-001", "status": "PAID"},
            {"orderId": "ORD-002", "status": "PENDING"}
        ]
        expect(orders).should("""
            = | orderId  | status   |
              | ORD-001  | PAID     |
              | ORD-002  | PENDING  |
        """)


class TestErrorCases:
    """错误情况测试"""
    
    def test_strict_equal_type_mismatch(self):
        """严格相等类型不匹配应失败"""
        with pytest.raises(AssertionError):
            expect(1).should("= 1.0")  # int != float
    
    def test_strict_object_extra_field(self):
        """严格模式有多余字段应失败"""
        user = {"name": "张三", "age": 25, "extra": "field"}
        with pytest.raises(AssertionError):
            expect(user).should("""
                = {
                    name: '张三'
                    age: 25
                }
            """)
    
    def test_missing_field(self):
        """缺少必需字段应失败"""
        user = {"name": "张三"}
        with pytest.raises(AssertionError):
            expect(user).should("""
                : {
                    name: '张三'
                    email: 'test@test.com'
                }
            """)


class TestChaining:
    """链式调用测试"""
    
    def test_should_chain(self):
        """should 方法应该支持链式调用"""
        user = {"name": "张三", "age": 25}
        expect(user).should(": { name: '张三' }").should(": { age: 25 }")
