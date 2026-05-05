"""
Schema 验证系统测试

对应 Java: DAL-java/src/test/resources/features/dal/verification/schema/*.feature
"""
import pytest
from datetime import datetime, timedelta
from core.dal.schema import (
    SchemaRegistry, SchemaValidationResult,
    register_schema, validate_schema, list_schemas
)
from core.dal import expect


class TestBuiltinSchemas:
    """测试内置 Schema"""
    
    def test_almost_now_with_datetime(self):
        """AlmostNow 验证当前时间"""
        result = validate_schema("AlmostNow", datetime.now())
        assert result.success is True
    
    def test_almost_now_with_timestamp(self):
        """AlmostNow 验证时间戳"""
        result = validate_schema("AlmostNow", datetime.now().timestamp())
        assert result.success is True
    
    def test_almost_now_with_old_time(self):
        """AlmostNow 验证过期时间应失败"""
        old_time = datetime.now() - timedelta(seconds=10)
        result = validate_schema("AlmostNow", old_time)
        assert result.success is False
    
    def test_instant_with_datetime(self):
        """Instant 验证 datetime"""
        result = validate_schema("Instant", datetime.now())
        assert result.success is True
    
    def test_instant_with_timestamp(self):
        """Instant 验证时间戳"""
        result = validate_schema("Instant", 1234567890)
        assert result.success is True
    
    def test_instant_with_iso_string(self):
        """Instant 验证 ISO 格式字符串"""
        result = validate_schema("Instant", "2024-01-01T00:00:00Z")
        assert result.success is True
    
    def test_instant_with_invalid(self):
        """Instant 验证无效值应失败"""
        result = validate_schema("Instant", "not a date")
        assert result.success is False
    
    def test_not_empty_with_string(self):
        """NotEmpty 验证非空字符串"""
        result = validate_schema("NotEmpty", "hello")
        assert result.success is True
    
    def test_not_empty_with_empty_string(self):
        """NotEmpty 验证空字符串应失败"""
        result = validate_schema("NotEmpty", "")
        assert result.success is False
    
    def test_not_empty_with_list(self):
        """NotEmpty 验证非空列表"""
        result = validate_schema("NotEmpty", [1, 2, 3])
        assert result.success is True
    
    def test_not_empty_with_empty_list(self):
        """NotEmpty 验证空列表应失败"""
        result = validate_schema("NotEmpty", [])
        assert result.success is False
    
    def test_not_empty_with_none(self):
        """NotEmpty 验证 None 应失败"""
        result = validate_schema("NotEmpty", None)
        assert result.success is False
    
    def test_not_null_with_value(self):
        """NotNull 验证非 null 值"""
        result = validate_schema("NotNull", "hello")
        assert result.success is True
    
    def test_not_null_with_none(self):
        """NotNull 验证 null 应失败"""
        result = validate_schema("NotNull", None)
        assert result.success is False
    
    def test_positive_with_positive_number(self):
        """Positive 验证正数"""
        result = validate_schema("Positive", 5)
        assert result.success is True
    
    def test_positive_with_zero(self):
        """Positive 验证零应失败"""
        result = validate_schema("Positive", 0)
        assert result.success is False
    
    def test_positive_with_negative(self):
        """Positive 验证负数应失败"""
        result = validate_schema("Positive", -5)
        assert result.success is False
    
    def test_negative_with_negative_number(self):
        """Negative 验证负数"""
        result = validate_schema("Negative", -5)
        assert result.success is True
    
    def test_non_negative_with_positive(self):
        """NonNegative 验证非负数"""
        result = validate_schema("NonNegative", 5)
        assert result.success is True
        result = validate_schema("NonNegative", 0)
        assert result.success is True
    
    def test_valid_email_with_valid(self):
        """ValidEmail 验证有效邮箱"""
        result = validate_schema("ValidEmail", "test@example.com")
        assert result.success is True
    
    def test_valid_email_with_invalid(self):
        """ValidEmail 验证无效邮箱应失败"""
        result = validate_schema("ValidEmail", "not-an-email")
        assert result.success is False
    
    def test_valid_url_with_valid(self):
        """ValidURL 验证有效 URL"""
        result = validate_schema("ValidURL", "https://example.com")
        assert result.success is True
    
    def test_valid_url_with_invalid(self):
        """ValidURL 验证无效 URL 应失败"""
        result = validate_schema("ValidURL", "not-a-url")
        assert result.success is False
    
    def test_valid_uuid_with_valid(self):
        """ValidUUID 验证有效 UUID"""
        result = validate_schema("ValidUUID", "550e8400-e29b-41d4-a716-446655440000")
        assert result.success is True
    
    def test_valid_uuid_with_invalid(self):
        """ValidUUID 验证无效 UUID 应失败"""
        result = validate_schema("ValidUUID", "not-a-uuid")
        assert result.success is False
    
    def test_string_with_string(self):
        """String 验证字符串类型"""
        result = validate_schema("String", "hello")
        assert result.success is True
    
    def test_string_with_number(self):
        """String 验证数字应失败"""
        result = validate_schema("String", 123)
        assert result.success is False
    
    def test_number_with_number(self):
        """Number 验证数字类型"""
        result = validate_schema("Number", 123)
        assert result.success is True
        result = validate_schema("Number", 1.5)
        assert result.success is True
    
    def test_number_with_string(self):
        """Number 验证字符串应失败"""
        result = validate_schema("Number", "123")
        assert result.success is False
    
    def test_integer_with_integer(self):
        """Integer 验证整数类型"""
        result = validate_schema("Integer", 123)
        assert result.success is True
    
    def test_integer_with_float(self):
        """Integer 验证浮点数应失败"""
        result = validate_schema("Integer", 1.5)
        assert result.success is False
    
    def test_boolean_with_boolean(self):
        """Boolean 验证布尔类型"""
        result = validate_schema("Boolean", True)
        assert result.success is True
    
    def test_boolean_with_string(self):
        """Boolean 验证字符串应失败"""
        result = validate_schema("Boolean", "true")
        assert result.success is False
    
    def test_array_with_list(self):
        """Array 验证列表类型"""
        result = validate_schema("Array", [1, 2, 3])
        assert result.success is True
    
    def test_array_with_string(self):
        """Array 验证字符串应失败"""
        result = validate_schema("Array", "not an array")
        assert result.success is False
    
    def test_object_with_dict(self):
        """Object 验证字典类型"""
        result = validate_schema("Object", {"key": "value"})
        assert result.success is True
    
    def test_object_with_string(self):
        """Object 验证字符串应失败"""
        result = validate_schema("Object", "not an object")
        assert result.success is False


class TestSchemaRegistry:
    """测试 Schema 注册表"""
    
    def test_register_custom_schema(self):
        """注册自定义 Schema"""
        registry = SchemaRegistry()
        
        @registry.register("CustomSchema")
        def custom_schema(value):
            return SchemaValidationResult(success=value > 0)
        
        result = registry.validate("CustomSchema", 5)
        assert result.success is True
        
        result = registry.validate("CustomSchema", -5)
        assert result.success is False
    
    def test_list_schemas(self):
        """列出所有 Schema"""
        schemas = list_schemas()
        assert "AlmostNow" in schemas
        assert "NotEmpty" in schemas
        assert "ValidEmail" in schemas
    
    def test_unknown_schema(self):
        """验证未知 Schema 应抛出异常"""
        registry = SchemaRegistry()
        with pytest.raises(ValueError, match="Unknown schema"):
            registry.validate("UnknownSchema", "value")


class TestSchemaWithDAL:
    """测试在 DAL 表达式中使用 Schema"""
    
    def test_is_schema_in_object(self):
        """在对象验证中使用 is Schema"""
        user = {
            "name": "张三",
            "email": "zhangsan@example.com",
            "age": 25
        }
        
        # 使用 is 进行 Schema 验证
        expect(user).should("""
            : {
                name is String
                email is ValidEmail
                age is Positive
            }
        """)
    
    def test_is_schema_with_not_empty(self):
        """使用 NotEmpty Schema"""
        data = {"value": "hello"}
        expect(data).should("""
            : {
                value is NotEmpty
            }
        """)
    
    def test_is_schema_with_number(self):
        """使用 Number Schema"""
        data = {"count": 10}
        expect(data).should("""
            : {
                count is Number
            }
        """)
    
    def test_is_schema_failure(self):
        """Schema 验证失败"""
        data = {"email": "not-an-email"}
        with pytest.raises(AssertionError):
            expect(data).should("""
                : {
                    email is ValidEmail
                }
            """)


class TestGlobalSchemaRegistration:
    """测试全局 Schema 注册"""
    
    def test_register_global_schema(self):
        """注册全局 Schema"""
        @register_schema("GlobalTestSchema")
        def global_test_schema(value):
            return SchemaValidationResult(success=value == "test")
        
        result = validate_schema("GlobalTestSchema", "test")
        assert result.success is True
        
        result = validate_schema("GlobalTestSchema", "other")
        assert result.success is False
