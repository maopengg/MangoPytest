---
name: "bdd-test-case-writer"
description: "Writes BDD test cases for MangoPytest framework using pytest-bdd and Gherkin Chinese syntax. Invoke when user asks to write automated test cases, add test scenarios, or implement BDD tests for API/UI testing."
---

# BDD Test Case Writer

This skill helps write BDD (Behavior-Driven Development) test cases for the MangoPytest framework.

## When to Invoke

- User asks to write automated test cases
- User wants to add new test scenarios
- User needs to implement BDD tests for API testing
- User requests to complete pending test cases
- User asks to convert test case documents to automated tests

## Framework Overview

MangoPytest uses a 5-layer architecture:

```
L5: Feature Files (Gherkin Chinese syntax)
    ↓
L4: Steps Layer (common/api/auth/data/assertions)
    ↓
L3: Data Factory (entities/factories/specs)
    ↓
L2: Repositories (business domain packages)
    ↓
L1: Database (MySQL)
```

## Writing Process

### Step 1: Analyze Requirements

1. Read the test case document (e.g., `mock/MockAPI测试用例.md`)
2. Identify the test case to implement
3. Note the API endpoint, method, parameters, and expected results

### Step 2: Write Feature File (L5)

**File location**: `auto_tests/bdd_api_mock/test_cases/<module>/test_<module>.feature`

**Template**:
```gherkin
# language: zh-CN
# -*- coding: utf-8 -*-
功能: <Module Name>
  作为<Role>
  我希望<Goal>
  以便<Purpose>

@<tag> @positive
场景: <Scenario Description>
  当 <Action>
  那么 <Expected Result>
  而且 <Additional Assertion>
```

**Common Tags**:
- `@smoke` - Smoke tests
- `@positive` - Positive tests
- `@negative` - Negative tests
- `@boundary` - Boundary value tests
- `@integration` - Integration tests

### Step 3: Write Step Definitions (L4)

**File location**: `auto_tests/bdd_api_mock/steps/<module>/<step_file>.py`

**Template for When steps**:
```python
@when(
    parsers.parse('<Gherkin pattern>'),
    target_fixture="<fixture_name>",
)
def <step_function_name>(<parameters>, api_client):
    """<Step description>"""
    log.debug(f"<Debug message>")
    response = api_client.<method>(
        "<endpoint>",
        {<request_body>}
    )
    log.debug(f"<Response log>: {response.data}")
    return response
```

**Template for Then steps**:
```python
@then(parsers.parse("<Expected result>"))
def <assertion_function_name>(<fixture_name>):
    """<Assertion description>"""
    response_data = (
        <fixture_name>.data if hasattr(<fixture_name>, "data") else <fixture_name>
    )
    assert <condition>, f"<Error message>"
```

### Step 4: Add pytest Markers (if needed)

**File location**: `auto_tests/bdd_api_mock/pytest.ini`

Add new markers if using custom tags:
```ini
markers =
    smoke: 冒烟测试
    positive: 正向测试
    negative: 负向测试
    boundary: 边界值测试
```

## Common Patterns

### Login Steps
```python
@when(
    parsers.parse('用户使用用户名"{username}"和密码"{password}"登录'),
    target_fixture="login_response",
)
def user_login_step(username: str, password: str, api_client):
    """User login step"""
    password_md5 = _hash_password(password)
    response = api_client.post(
        "/auth/login", 
        {"username": username, "password": password_md5}
    )
    return response
```

### Assertion Steps
```python
@then(parsers.parse("登录应该成功"))
def login_should_succeed(login_response):
    """Verify login success"""
    response_data = (
        login_response.data if hasattr(login_response, "data") else login_response
    )
    assert response_data.get("code") == 200

@then(parsers.parse('应该返回错误码 {error_code:d}'))
def should_return_error_code(error_code: int, login_response):
    """Verify error code"""
    response_data = (
        login_response.data if hasattr(login_response, "data") else login_response
    )
    assert response_data.get("code") == error_code
```

### Data Generation
```python
from mangotools.data_processor import DataProcessor

_data_processor = DataProcessor()

# Generate test data
email = _data_processor.character_email()
name = _data_processor.character_male_name()
phone = _data_processor.character_phone()
uuid_str = _data_processor.str_uuid_no_dash()
```

## File Structure

```
auto_tests/bdd_api_mock/
├── test_cases/
│   └── <module>/
│       ├── test_<module>.feature    # L5: Gherkin scenarios
│       └── test_<module>.py         # BDD binding file
├── steps/
│   └── <module>/
│       └── <step_file>.py           # L4: Step definitions
├── data_factory/
│   ├── entities/                    # L3: Pydantic entities
│   └── specs/                       # L3: Factory specs
└── repos/                           # L2: Data repositories
```

## Running Tests

```bash
# Run specific test file
.venv\Scripts\python -m pytest auto_tests\bdd_api_mock\test_cases\auth\test_auth.py -v

# Run by tags
.venv\Scripts\python -m pytest auto_tests\bdd_api_mock\test_cases\auth\test_auth.py -v -m "smoke"

# Run all tests
.venv\Scripts\python -m pytest auto_tests\bdd_api_mock\ -v
```

## Best Practices

1. **Use Chinese Gherkin syntax** with `# language: zh-CN`
2. **Add appropriate tags** for test categorization
3. **Use log.debug()** for detailed logging
4. **Generate random data** for unique values (usernames, emails)
5. **Return response objects** from When steps for assertions
6. **Write clear error messages** in assertions
7. **Follow existing patterns** in the codebase

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Marker not found | Add marker to pytest.ini |
| KeyError: 'response' | Check fixture return structure |
| Username already exists | Use random username generation |
| Missing required fields | Check API documentation for all required fields |
| Assertion failures | Verify expected vs actual values in logs |

## Example: Complete Test Case

**Feature File**:
```gherkin
# language: zh-CN
功能: 用户认证
  @positive
  场景: 使用明文密码登录成功
    当 用户使用用户名"testuser"和明文密码"password123"登录
    那么 登录应该成功
```

**Step Definition**:
```python
@when(
    parsers.parse('用户使用用户名"{username}"和明文密码"{password}"登录'),
    target_fixture="login_response",
)
def user_login_with_plain_password_step(username: str, password: str, api_client):
    """用户使用明文密码登录步骤"""
    log.debug(f"使用明文密码登录: {username}")
    response = api_client.post(
        "/auth/login", {"username": username, "password": password}
    )
    log.debug(f"明文密码登录响应: {response.data}")
    return response
```

**Assertion**:
```python
@then(parsers.parse("登录应该成功"))
def login_should_succeed(login_response):
    """验证登录成功"""
    response_data = (
        login_response.data if hasattr(login_response, "data") else login_response
    )
    assert response_data.get("code") == 200
```
