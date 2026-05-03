# Fixtures — 公共 Fixture 设计

## 职责

提供浏览器驱动、页面上下文、测试数据共享等基础设施 fixture。

## 目录结构

```
fixtures/
├── bdd.py        # 浏览器驱动 + 页面上下文 + 步骤共享 fixture
└── clients.py    # UI 配置
```

## 写法

### 浏览器驱动（`fixtures/bdd.py`）

```python
@pytest.fixture(scope="session")
def driver_object():
    """Session 级别，整个测试会话共享一个浏览器实例"""
    driver = DriverObject(log)
    driver.set_web(web_type=BrowserTypeEnum.CHROMIUM.value, web_max=True)
    yield driver
    try:
        driver.web.close()
    except Exception:
        pass
```

### 页面上下文（`fixtures/bdd.py`）

```python
@pytest.fixture(scope="function")
def base_data(driver_object):
    """Function 级别，每个测试独立的页面上下文"""
    context, page = driver_object.web.new_web_page()
    test_data = ObtainTestData()
    base_data_obj = BaseDataDrives(test_data, log)
    base_data_obj.set_page_context(page, context)
    base_data_obj.set_file_path(
        project_dir.download(), project_dir.screenshot()
    )
    yield base_data_obj
    try:
        context.close()
        page.close()
    except Exception as e:
        log.debug(f"清理页面上下文时出错: {e}")
```

### 步骤间共享数据（`fixtures/bdd.py`）

```python
@pytest.fixture
def page_context():
    """步骤间传递 Page Object 实例"""
    return {}

@pytest.fixture
def test_data_context():
    """步骤间传递业务数据"""
    return {}

@pytest.fixture
def logged_in_user(base_data):
    """BDD 步骤统一入口，包装 base_data"""
    return {"base_data": base_data}
```

### UI 配置（`fixtures/clients.py`）

```python
@pytest.fixture(scope="session")
def ui_config():
    from auto_tests.<project>.config import settings
    return settings
```

## 作用域选择

| scope | fixture | 说明 |
|-------|---------|------|
| `session` | `driver_object` | 浏览器只启动一次 |
| `session` | `db_session` | 数据库连接复用 |
| `function` | `base_data` | 每个测试独立页面，互不干扰 |
| `function` | `page_context` | 每个测试独立上下文 |
| `function` | `test_data_context` | 每个测试独立数据 |
