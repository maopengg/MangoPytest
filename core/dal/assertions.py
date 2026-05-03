"""
断言 API - 对外暴露的 DAL 断言接口

提供类似 Java TestCharm 的 expect/should API
"""

from typing import Any, Union
from .core.lexer import Lexer, tokenize
from .core.parser import Parser, parse_expression
from .core.runtime import DALRuntime, RuntimeContext, evaluate
from .core.ast_nodes import Expression, ObjectLiteral, ArrayLiteral, TableExpression, ExistsCheck, BinaryOp, Identifier, SchemaExpression, Wildcard, StringLiteral


class Expectation:
    """
    期望对象，用于链式调用
    
    Example:
        >>> expect(user).should(": { name: '张三', age: > 18 }")
        >>> expect(orders).should("| orderId | status |")
    """
    
    def __init__(self, actual: Any):
        """
        创建期望对象
        
        Args:
            actual: 要验证的实际值
        """
        self.actual = actual
        self.context = RuntimeContext(actual)
        self.runtime = DALRuntime(self.context)
    
    def should(self, expression: str) -> "Expectation":
        """
        验证数据是否符合 DAL 表达式
        
        Args:
            expression: DAL 表达式字符串
            
        Returns:
            self，支持链式调用
            
        Raises:
            AssertionError: 验证失败时抛出
            
        Example:
            >>> expect({"name": "张三"}).should(": { name: '张三' }")
            >>> expect([1, 2, 3]).should(".size = 3")
        """
        # 检查是否包含 ::eventually，如果包含则进行轮询
        if "::eventually" in expression:
            return self._should_eventually(expression)

        # 解析表达式
        try:
            ast = parse_expression(expression)
        except Exception as e:
            raise AssertionError(f"Failed to parse expression: {expression}\nError: {e}")

        # 特殊处理：如果是对象/数组/表格字面量，进行验证而不是求值
        # 也处理 BinaryOp（如 root : ObjectLiteral）的情况
        from .core.ast_nodes import BinaryOp
        is_complex = isinstance(ast, (ObjectLiteral, ArrayLiteral, TableExpression))
        # 松散匹配操作符 : 进行复杂类型验证
        is_binary_loose = isinstance(ast, BinaryOp) and ast.operator == ":" and isinstance(ast.right, (ObjectLiteral, ArrayLiteral, TableExpression))
        # 严格匹配操作符 = 只有在右边是表格时才进行验证（表格不支持 =[] 或 ={} 语法）
        is_binary_strict_table = isinstance(ast, BinaryOp) and ast.operator == "=" and isinstance(ast.right, TableExpression)

        if is_complex or is_binary_loose or is_binary_strict_table:
            result = self._verify_complex(ast)
        else:
            # 普通表达式求值
            result = self.runtime.evaluate(ast)

        # 验证失败或结果为 False 时抛出异常
        if not result.success or not result.value:
            raise AssertionError(self._format_error(expression, result))

        return self

    def _should_eventually(self, expression: str, timeout: float = 5.0, interval: float = 0.5) -> "Expectation":
        """
        异步等待验证：轮询等待某个条件成立

        Args:
            expression: DAL 表达式字符串（包含 ::eventually）
            timeout: 最大等待时间（秒）
            interval: 轮询间隔（秒）

        Returns:
            self，支持链式调用

        Raises:
            AssertionError: 超时后条件仍未成立时抛出

        Example:
            >>> expect(data).should("::eventually ::size = 5")  # 等待 data 的 size 等于 5
        """
        import time

        # 移除 ::eventually 后的表达式
        actual_expression = expression.replace("::eventually", "").strip()

        start_time = time.time()
        last_error = None

        while time.time() - start_time < timeout:
            try:
                # 尝试验证
                ast = parse_expression(actual_expression)
                from .core.ast_nodes import BinaryOp
                is_complex = isinstance(ast, (ObjectLiteral, ArrayLiteral, TableExpression))
                is_binary_loose = isinstance(ast, BinaryOp) and ast.operator == ":" and isinstance(ast.right, (ObjectLiteral, ArrayLiteral, TableExpression))
                is_binary_strict_table = isinstance(ast, BinaryOp) and ast.operator == "=" and isinstance(ast.right, TableExpression)

                if is_complex or is_binary_loose or is_binary_strict_table:
                    result = self._verify_complex(ast)
                else:
                    result = self.runtime.evaluate(ast)

                if result.success and result.value:
                    return self

                last_error = result
            except Exception as e:
                last_error = e

            # 等待一段时间后重试
            time.sleep(interval)

        # 超时，抛出异常
        raise AssertionError(f"Eventually timeout after {timeout}s: condition not met\nExpression: {actual_expression}\nLast error: {last_error}")
    
    def should_not(self, expression: str) -> "Expectation":
        """
        反向验证：数据不应该符合表达式
        
        Args:
            expression: DAL 表达式字符串
            
        Returns:
            self，支持链式调用
            
        Raises:
            AssertionError: 验证通过时抛出（即实际应该失败）
        """
        try:
            self.should(expression)
            raise AssertionError(f"Expected NOT to match expression, but it did: {expression}")
        except AssertionError:
            # 预期的失败
            pass
        
        return self
    
    def _verify_complex(self, ast: Expression) -> Any:
        """
        验证复杂类型（对象、数组、表格）
        
        Args:
            ast: AST 节点
            
        Returns:
            验证结果
        """
        from .core.runtime import EvaluationResult
        from .core.ast_nodes import BinaryOp
        
        # 处理 BinaryOp（如 root : ObjectLiteral）
        if isinstance(ast, BinaryOp):
            if isinstance(ast.right, ObjectLiteral):
                return self._verify_object(ast.right)
            elif isinstance(ast.right, ArrayLiteral):
                return self._verify_array(ast.right)
            elif isinstance(ast.right, TableExpression):
                return self._verify_table(ast.right)
        
        if isinstance(ast, ObjectLiteral):
            return self._verify_object(ast)
        elif isinstance(ast, ArrayLiteral):
            return self._verify_array(ast)
        elif isinstance(ast, TableExpression):
            return self._verify_table(ast)
        
        return EvaluationResult.ok(True)
    
    def _verify_object(self, obj_lit: ObjectLiteral) -> Any:
        """验证对象"""
        from .core.runtime import EvaluationResult
        from .core.operators import Operators, compare
        
        actual = self.actual
        
        # 检查是否为字典
        if not isinstance(actual, dict):
            return EvaluationResult.fail(
                expected="object",
                actual=type(actual).__name__,
                message=f"Expected object, got {type(actual).__name__}"
            )
        
        # 严格模式：检查是否有额外字段
        if obj_lit.strict:
            expected_keys = {prop.key for prop in obj_lit.properties}
            actual_keys = set(actual.keys())
            extra_keys = actual_keys - expected_keys
            if extra_keys:
                return EvaluationResult.fail(
                    expected=f"fields {expected_keys}",
                    actual=f"fields {actual_keys}",
                    message=f"Unexpected fields: {extra_keys}"
                )
        
        # 验证每个属性
        for prop in obj_lit.properties:
            key = prop.key
            
            # 处理嵌套属性（如 address.city）
            key_parts = key.split('.')
            
            # 获取实际值（支持嵌套访问）
            try:
                actual_value = actual
                for part in key_parts:
                    if isinstance(actual_value, dict):
                        if part not in actual_value:
                            raise KeyError(part)
                        actual_value = actual_value[part]
                    else:
                        raise KeyError(part)
            except (KeyError, TypeError):
                # 字段不存在
                if isinstance(prop.value, ExistsCheck):
                    # 存在性检查：根据 ExistsCheck.optional 决定是否跳过
                    if prop.value.optional:
                        continue  # 可选字段，不存在也检查通过
                    else:
                        # 必须存在的字段不存在，检查失败
                        return EvaluationResult.fail(
                            expected=f"property '{key}' to exist",
                            actual="not found",
                            path=key,
                            message=f"Property '{key}' not found"
                        )
                
                # 普通属性缺失
                return EvaluationResult.fail(
                    expected=f"property '{key}'",
                    actual="not found",
                    path=key,
                    message=f"Property '{key}' not found"
                )
            
            # 检查是否是存在性检查
            if isinstance(prop.value, ExistsCheck):
                continue  # 已经确认字段存在
            
            # 如果只是存在性检查（没有值表达式）
            if isinstance(prop.value, Expression) and hasattr(prop.value, 'value') and prop.value.value is None:
                continue
            
            # 处理属性值是 Wildcard 的情况（如 name: *）
            if isinstance(prop.value, Wildcard):
                from .core.runtime import DALRuntime
                # 创建临时运行时来验证通配符
                wildcard_context = RuntimeContext(actual_value)
                wildcard_context.schemas = self.context.schemas
                wildcard_runtime = DALRuntime(wildcard_context)
                wildcard_result = wildcard_runtime.evaluate(prop.value)
                if not wildcard_result.success or not wildcard_result.value:
                    return EvaluationResult.fail(
                        expected=f"{key} matches wildcard {'*' * prop.value.level}",
                        actual=str(actual_value),
                        path=key,
                        message=wildcard_result.message or f"Wildcard {'*' * prop.value.level} does not match"
                    )
                continue

            # 处理属性值是 SchemaExpression 的情况（如 name is String）
            if isinstance(prop.value, SchemaExpression):
                from .schema import validate_schema
                schema_result = validate_schema(prop.value.schema_name, actual_value)
                if not schema_result.success:
                    return EvaluationResult.fail(
                        expected=f"Schema '{prop.value.schema_name}'",
                        actual=str(actual_value),
                        path=key,
                        message=schema_result.message
                    )

                # 处理 which 子句（如 name is String which {...}）
                if prop.value.base is not None:
                    # which 子句应该是一个对象表达式，用于进一步验证
                    # 创建一个新的运行时上下文来验证 which 子句
                    which_context = RuntimeContext(actual_value)
                    which_context.schemas = self.context.schemas
                    which_runtime = DALRuntime(which_context)
                    which_result = which_runtime.evaluate(prop.value.base)
                    if not which_result.success:
                        return EvaluationResult.fail(
                            expected=f"Schema '{prop.value.schema_name}' with conditions",
                            actual=str(actual_value),
                            path=key,
                            message=which_result.message or "Schema which clause validation failed"
                        )

                continue
            
            # 处理属性值是 BinaryOp 的情况（如 age: > 18）
            # 需要将 BinaryOp 的左操作数从 root 替换为实际值
            if isinstance(prop.value, BinaryOp) and isinstance(prop.value.left, Identifier) and prop.value.left.name == "root":
                # 创建新的 BinaryOp，左操作数替换为实际值
                from .core.ast_nodes import NumberLiteral, StringLiteral, BooleanLiteral, NullLiteral
                
                # 将实际值转换为 Literal
                if isinstance(actual_value, bool):
                    left_literal = BooleanLiteral(actual_value)
                elif isinstance(actual_value, (int, float)):
                    left_literal = NumberLiteral(actual_value)
                elif isinstance(actual_value, str):
                    left_literal = StringLiteral(actual_value)
                elif actual_value is None:
                    left_literal = NullLiteral()
                else:
                    # 对于复杂类型，使用原始值
                    left_literal = Identifier(str(actual_value))
                
                new_binary = BinaryOp(left_literal, prop.value.operator, prop.value.right)
                prop_result = self.runtime.evaluate(new_binary)
                
                # 对于比较表达式，直接使用求值结果
                if not prop_result.success:
                    return EvaluationResult.fail(
                        expected=f"{key} {prop.value.operator} {prop.value.right}",
                        actual=str(actual_value),
                        path=key,
                        message=f"Comparison failed: {actual_value} {prop.value.operator} ..."
                    )
                continue
            else:
                # 求值期望表达式
                prop_result = self.runtime.evaluate(prop.value)
            
            if not prop_result.success:
                return prop_result
            
            expected_value = prop_result.value
            
            # 比较
            result = compare(prop.operator, actual_value, expected_value)
            if not result.success:
                return EvaluationResult.fail(
                    expected=f"{key} {prop.operator} {result.expected}",
                    actual=str(actual_value),
                    path=key,
                    message=result.message
                )
        
        return EvaluationResult.ok(True)
    
    def _verify_array(self, arr_lit: ArrayLiteral) -> Any:
        """验证数组"""
        from .core.runtime import EvaluationResult
        from .core.operators import compare
        
        actual = self.actual
        
        # 检查是否为列表
        if not isinstance(actual, list):
            return EvaluationResult.fail(
                expected="list",
                actual=type(actual).__name__,
                message=f"Expected list, got {type(actual).__name__}"
            )
        
        # 严格模式：检查长度
        if arr_lit.strict and len(actual) != len(arr_lit.elements):
            return EvaluationResult.fail(
                expected=f"list of size {len(arr_lit.elements)}",
                actual=f"list of size {len(actual)}",
                message=f"List size mismatch: expected {len(arr_lit.elements)}, got {len(actual)}"
            )
        
        # 验证每个元素
        for i, elem in enumerate(arr_lit.elements):
            if i >= len(actual):
                return EvaluationResult.fail(
                    expected=f"element at index {i}",
                    actual="index out of range",
                    path=f"[{i}]",
                    message=f"Index {i} out of range"
                )
            
            actual_value = actual[i]

            # 处理元素是 Wildcard 的情况
            if isinstance(elem, Wildcard):
                from .core.runtime import DALRuntime
                wildcard_context = RuntimeContext(actual_value)
                wildcard_context.schemas = self.context.schemas
                wildcard_runtime = DALRuntime(wildcard_context)
                wildcard_result = wildcard_runtime.evaluate(elem)
                if not wildcard_result.success or not wildcard_result.value:
                    return EvaluationResult.fail(
                        expected=f"element at [{i}] matches wildcard {'*' * elem.level}",
                        actual=str(actual_value),
                        path=f"[{i}]",
                        message=wildcard_result.message or f"Wildcard {'*' * elem.level} does not match"
                    )
                continue

            # 处理元素是 ObjectLiteral 的情况
            if isinstance(elem, ObjectLiteral):
                # 创建临时 Expectation 来验证对象
                from .core.runtime import DALRuntime
                obj_context = RuntimeContext(actual_value)
                obj_context.schemas = self.context.schemas
                obj_runtime = DALRuntime(obj_context)
                obj_expectation = Expectation(actual_value)
                obj_expectation.context = obj_context
                obj_expectation.runtime = obj_runtime
                obj_result = obj_expectation._verify_object(elem)
                if not obj_result.success:
                    obj_result.path = f"[{i}]"
                    return obj_result
                continue

            # 求值期望表达式
            elem_result = self.runtime.evaluate(elem)
            if not elem_result.success:
                return elem_result

            expected_value = elem_result.value

            # 比较
            result = compare("=", actual_value, expected_value)
            if not result.success:
                return EvaluationResult.fail(
                    expected=f"[{i}] = {result.expected}",
                    actual=str(actual_value),
                    path=f"[{i}]",
                    message=result.message
                )
        
        return EvaluationResult.ok(True)
    
    def _verify_table(self, table: TableExpression) -> Any:
        """验证表格"""
        from .core.runtime import EvaluationResult
        from .core.operators import compare
        
        actual = self.actual
        
        # 检查是否为列表
        if not isinstance(actual, list):
            return EvaluationResult.fail(
                expected="list",
                actual=type(actual).__name__,
                message=f"Expected list for table verification, got {type(actual).__name__}"
            )
        
        # 处理转置
        if table.transpose:
            # 转置表格：表头变成第一列，数据行变成列
            return self._verify_table_transposed(table, actual)
        
        # 应用排序
        actual_data = actual
        if table.sort_by and table.sort_by in table.headers:
            sort_idx = table.headers.index(table.sort_by)
            # 对期望行排序
            sorted_rows = sorted(
                enumerate(table.rows),
                key=lambda x: self._get_cell_sort_key(x[1][sort_idx]),
                reverse=table.sort_desc
            )
            sorted_row_indices = [x[0] for x in sorted_rows]
            # 对实际数据排序
            if all(isinstance(row, dict) and table.sort_by in row for row in actual_data):
                actual_data = sorted(
                    actual_data,
                    key=lambda x: x.get(table.sort_by),
                    reverse=table.sort_desc
                )
        else:
            sorted_row_indices = list(range(len(table.rows)))
        
        # 应用 skip（在排序之后）
        if table.skip > 0:
            actual_data = actual_data[table.skip:]
        
        # 验证行数
        if len(actual_data) != len(table.rows):
            return EvaluationResult.fail(
                expected=f"{len(table.rows)} rows",
                actual=f"{len(actual_data)} rows",
                message=f"Row count mismatch: expected {len(table.rows)}, got {len(actual_data)}"
            )
        
        # 验证每一行
        for row_idx, actual_row_idx in enumerate(sorted_row_indices):
            row = table.rows[actual_row_idx]
            actual_row = actual_data[row_idx]
            
            # 检查是否为字典
            if not isinstance(actual_row, dict):
                return EvaluationResult.fail(
                    expected=f"object at row {row_idx}",
                    actual=type(actual_row).__name__,
                    path=f"[{row_idx}]",
                    message=f"Expected object at row {row_idx}, got {type(actual_row).__name__}"
                )
            
            # 处理行标题（第一列作为标识符）
            start_col = 1 if table.row_header else 0
            
            # 验证每个单元格
            for col_idx, (header, cell) in enumerate(zip(table.headers[start_col:], row[start_col:]), start=start_col):
                if header not in actual_row:
                    return EvaluationResult.fail(
                        expected=f"column '{header}'",
                        actual="not found",
                        path=f"[{row_idx}].{header}",
                        message=f"Column '{header}' not found at row {row_idx}"
                    )
                
                actual_value = actual_row[header]
                
                # 求值期望表达式
                cell_result = self.runtime.evaluate(cell)
                if not cell_result.success:
                    return cell_result
                
                expected_value = cell_result.value
                
                # 比较
                result = compare("=", actual_value, expected_value)
                if not result.success:
                    return EvaluationResult.fail(
                        expected=f"[{row_idx}].{header} = {result.expected}",
                        actual=str(actual_value),
                        path=f"[{row_idx}].{header}",
                        message=result.message
                    )
        
        return EvaluationResult.ok(True)
    
    def _get_cell_sort_key(self, cell):
        """获取单元格排序键"""
        from .core.ast_nodes import NumberLiteral, StringLiteral
        if isinstance(cell, NumberLiteral):
            return cell.value
        elif isinstance(cell, StringLiteral):
            return cell.value
        else:
            return str(cell)
    
    def _verify_table_transposed(self, table: TableExpression, actual: list) -> Any:
        """验证转置表格"""
        from .core.runtime import EvaluationResult
        from .core.operators import compare

        # 转置后：原表头变成第一列，原数据行变成列
        # 实际数据应该是列表的列表

        # 检查是否为列表
        if not isinstance(actual, list):
            return EvaluationResult.fail(
                expected="list for transposed table",
                actual=type(actual).__name__,
                message=f"Expected list for transposed table verification, got {type(actual).__name__}"
            )

        # 构建期望的转置数据结构
        # 原表头: [name, age, city]
        # 原数据: [[Alice, 25, NYC], [Bob, 30, LA]]
        # 转置后期望: [[name, Alice, Bob], [age, 25, 30], [city, NYC, LA]]

        # 首先构建原始表格结构
        # 表头是字符串，需要转换为 StringLiteral
        header_literals = [StringLiteral(h) for h in table.headers]
        expected_rows = [header_literals] + table.rows  # 包含表头的所有行

        # 转置期望数据
        if expected_rows and expected_rows[0]:
            transposed = []
            num_cols = len(expected_rows[0])
            num_rows = len(expected_rows)
            for col_idx in range(num_cols):
                new_row = []
                for row_idx in range(num_rows):
                    if col_idx < len(expected_rows[row_idx]):
                        new_row.append(expected_rows[row_idx][col_idx])
                    else:
                        new_row.append(StringLiteral(""))
                transposed.append(new_row)
        else:
            transposed = []

        # 应用 skip
        actual_data = actual
        if table.skip > 0:
            actual_data = actual_data[table.skip:]

        # 验证行数
        if len(actual_data) != len(transposed):
            return EvaluationResult.fail(
                expected=f"{len(transposed)} rows in transposed table",
                actual=f"{len(actual_data)} rows",
                message=f"Row count mismatch in transposed table: expected {len(transposed)}, got {len(actual_data)}"
            )

        # 验证每一行
        for row_idx, (expected_row, actual_row) in enumerate(zip(transposed, actual_data)):
            # 检查实际行是否为列表
            if not isinstance(actual_row, list):
                return EvaluationResult.fail(
                    expected=f"list at row {row_idx}",
                    actual=type(actual_row).__name__,
                    path=f"[{row_idx}]",
                    message=f"Expected list at row {row_idx}, got {type(actual_row).__name__}"
                )

            # 验证列数
            if len(actual_row) != len(expected_row):
                return EvaluationResult.fail(
                    expected=f"{len(expected_row)} columns at row {row_idx}",
                    actual=f"{len(actual_row)} columns",
                    path=f"[{row_idx}]",
                    message=f"Column count mismatch at row {row_idx}: expected {len(expected_row)}, got {len(actual_row)}"
                )

            # 验证每个单元格
            for col_idx, (expected_cell, actual_value) in enumerate(zip(expected_row, actual_row)):
                # 求值期望表达式
                cell_result = self.runtime.evaluate(expected_cell)
                if not cell_result.success:
                    return cell_result

                expected_value = cell_result.value

                # 比较
                result = compare("=", actual_value, expected_value)
                if not result.success:
                    return EvaluationResult.fail(
                        expected=f"[{row_idx}][{col_idx}] = {result.expected}",
                        actual=str(actual_value),
                        path=f"[{row_idx}][{col_idx}]",
                        message=result.message
                    )

        return EvaluationResult.ok(True)
    
    def _format_error(self, expression: str, result: Any) -> str:
        """格式化错误信息"""
        lines = [
            "DAL assertion failed",
            f"  Expression: {expression}",
        ]
        
        if result.path:
            lines.append(f"  Path: {result.path}")
        
        if result.expected:
            lines.append(f"  Expected: {result.expected}")
        
        if result.actual:
            lines.append(f"  Actual: {result.actual}")
        
        if result.message:
            lines.append(f"  Message: {result.message}")
        
        return "\n".join(lines)


def expect(actual: Any) -> Expectation:
    """
    创建期望对象，开始 DAL 断言
    
    Args:
        actual: 要验证的实际值
        
    Returns:
        Expectation 对象
        
    Example:
        >>> expect({"name": "张三", "age": 25}).should(": { name: '张三', age: > 18 }")
        >>> expect([1, 2, 3]).should(".size = 3")
        >>> expect("hello").should("= 'hello'")
    """
    return Expectation(actual)


# 便捷函数
def assert_that(actual: Any, expression: str):
    """
    便捷断言函数
    
    Args:
        actual: 实际值
        expression: DAL 表达式
        
    Raises:
        AssertionError: 验证失败时抛出
    """
    expect(actual).should(expression)
