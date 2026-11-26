"""
表格高级功能测试

测试表格排序、跳过、行标题等功能
"""
import pytest
from core.dal import expect, CompareResult


class TestTableSort:
    """表格排序测试"""
    
    def test_table_sort_ascending(self):
        """表格升序排序"""
        data = [
            {"id": 3, "name": "C"},
            {"id": 1, "name": "A"},
            {"id": 2, "name": "B"}
        ]
        
        expect(data).should("""
            | id | name | sort by id asc |
            | 1  | A    |
            | 2  | B    |
            | 3  | C    |
        """)
    
    def test_table_sort_descending(self):
        """表格降序排序"""
        data = [
            {"id": 1, "name": "A"},
            {"id": 3, "name": "C"},
            {"id": 2, "name": "B"}
        ]
        
        expect(data).should("""
            | id | name | sort by id desc |
            | 3  | C    |
            | 2  | B    |
            | 1  | A    |
        """)
    
    def test_table_sort_by_name(self):
        """按名称排序"""
        data = [
            {"id": 1, "name": "Charlie"},
            {"id": 2, "name": "Alice"},
            {"id": 3, "name": "Bob"}
        ]
        
        expect(data).should("""
            | id | name    | sort by name asc |
            | 2  | Alice   |
            | 3  | Bob     |
            | 1  | Charlie |
        """)


class TestTableSkip:
    """表格跳过测试"""
    
    def test_table_skip_rows(self):
        """跳过前几行"""
        data = [
            {"id": 1, "name": "First"},
            {"id": 2, "name": "Second"},
            {"id": 3, "name": "Third"},
            {"id": 4, "name": "Fourth"}
        ]
        
        # 跳过前2行，验证后2行
        expect(data).should("""
            | id | name   | skip 2 |
            | 3  | Third  |
            | 4  | Fourth |
        """)
    
    def test_table_skip_zero(self):
        """skip 0 不跳过任何行"""
        data = [
            {"id": 1, "name": "First"},
            {"id": 2, "name": "Second"}
        ]
        
        expect(data).should("""
            | id | name    | skip 0 |
            | 1  | First   |
            | 2  | Second  |
        """)


class TestTableRowHeader:
    """表格行标题测试"""
    
    def test_table_row_header(self):
        """第一列作为行标题（不参与验证）"""
        data = [
            {"row_id": "row1", "value": 100},
            {"row_id": "row2", "value": 200}
        ]
        
        # row_id 列作为行标题，不验证其值
        expect(data).should("""
            | row_id | value | row header |
            | row1   | 100   |
            | row2   | 200   |
        """)
    
    def test_table_row_header_different_values(self):
        """行标题列可以有不同值"""
        data = [
            {"id": "A", "name": "Test", "status": "active"},
            {"id": "B", "name": "Test", "status": "active"}
        ]
        
        # id 列作为行标题，name 和 status 列验证
        expect(data).should("""
            | id | name | status | row header |
            | X  | Test | active |
            | Y  | Test | active |
        """)


class TestTableCombinedOptions:
    """表格组合选项测试"""
    
    def test_table_sort_and_skip(self):
        """排序和跳过组合"""
        data = [
            {"id": 4, "name": "D"},
            {"id": 1, "name": "A"},
            {"id": 3, "name": "C"},
            {"id": 2, "name": "B"}
        ]
        
        # 先排序，再跳过前1行
        expect(data).should("""
            | id | name | sort by id asc skip 1 |
            | 2  | B    |
            | 3  | C    |
            | 4  | D    |
        """)


class TestCustomOperator:
    """自定义操作符测试"""
    
    def test_register_custom_operator(self):
        """注册并使用自定义操作符"""
        from core.dal import Operators, CompareResult
        
        # 注册自定义操作符 has（包含匹配）
        # 注意：contains 已经是内置关键字，使用 has 作为自定义操作符
        @Operators.register("has")
        def has_match(actual, expected):
            """检查 actual 是否包含 expected"""
            if isinstance(actual, str) and isinstance(expected, str):
                success = expected in actual
                return CompareResult(
                    success=success,
                    expected=f"has '{expected}'",
                    actual=str(actual),
                    message=f"'{expected}' not found in '{actual}'" if not success else ""
                )
            return CompareResult(
                success=False,
                expected=f"string containing '{expected}'",
                actual=str(actual),
                message="Type mismatch"
            )
        
        try:
            # 使用自定义操作符 - 由于 has 不是关键字，直接使用 compare 函数测试
            from core.dal.core.operators import compare
            result = compare("has", "hello world", "world")
            assert result.success is True
            result = compare("has", "hello world", "hello")
            assert result.success is True
            result = compare("has", "hello world", "foo")
            assert result.success is False
        finally:
            # 清理
            Operators.unregister("has")
    
    def test_custom_operator_case_insensitive(self):
        """自定义操作符 - 不区分大小写匹配"""
        from core.dal import Operators, CompareResult
        
        # 注册 icontains 操作符（不区分大小写包含）
        # 注意：icontains 不是关键字，需要使用标准操作符语法
        @Operators.register("icontains")
        def case_insensitive_match(actual, expected):
            """不区分大小写包含匹配"""
            if isinstance(actual, str) and isinstance(expected, str):
                success = expected.lower() in actual.lower()
                return CompareResult(
                    success=success,
                    expected=f"contains '{expected}' (case insensitive)",
                    actual=str(actual),
                    message=f"'{expected}' not found in '{actual}' (case insensitive)" if not success else ""
                )
            return CompareResult(
                success=False,
                expected=f"string containing '{expected}'",
                actual=str(actual),
                message="Type mismatch"
            )
        
        try:
            # 使用 : 操作符配合自定义操作符名称
            # 由于 icontains 不是关键字，需要使用不同的语法
            # 这里我们直接使用 Operators.compare 来测试
            from core.dal.core.operators import compare
            result = compare("icontains", "Hello World", "hello")
            assert result.success is True
            result = compare("icontains", "Hello World", "WORLD")
            assert result.success is True
        finally:
            Operators.unregister("icontains")
    
    def test_list_custom_operators(self):
        """列出自定义操作符"""
        from core.dal import Operators
        
        @Operators.register("test_op")
        def test_op(actual, expected):
            return CompareResult(success=True, expected="test", actual="test")
        
        try:
            ops = Operators.list_custom()
            assert "test_op" in ops
        finally:
            Operators.unregister("test_op")
