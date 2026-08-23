# API Client — BDD 兼容客户端设计

## 职责

封装 HTTP 请求，提供 BDD 步骤兼容的 Dict 返回格式。

## 设计思路

BDD 步骤期望 `api_response` 是 Dict 类型，标准的 core APIClient 返回 `APIResponse` 对象。本项目包装一层，返回 Dict。

## 写法

### 核心包装

```python
class APIClient:
    def __init__(self, base_url=None):
        self.base_url = (base_url or settings.BASE_URL).rstrip("/")
        self._client = httpx.Client(timeout=30)

    def get(self, path, created_entity=None, **kwargs) -> dict:
        url = self._prepare_url(path, created_entity)  # 替换 ${entity.id}
        response = self._client.get(url, **kwargs)
        return {"code": response.status_code, "data": response.json()}

    def post(self, path, body=None, created_entity=None, **kwargs) -> dict:
        url = self._prepare_url(path, created_entity)
        body = self._prepare_body(body, created_entity)
        response = self._client.post(url, json=body, **kwargs)
        return {"code": response.status_code, "data": response.json()}
```

### 占位符替换

Feature 文件中的 `${user.id}` 在请求前替换为实际值：

```python
def _prepare_url(self, path, created_entity):
    if created_entity:
        path = re.sub(r"\$\{(\w+)\.id\}", str(created_entity["id"]), path)
    return f"{self.base_url}/{path.lstrip('/')}"

def _prepare_body(self, body, created_entity):
    if created_entity and body:
        body_str = json.dumps(body)
        body_str = re.sub(r"\$\{(\w+)\.id\}", str(created_entity["id"]), body_str)
        return json.loads(body_str)
    return body
```

## 与 core APIClient 的关系

| | core APIClient | BDD APIClient |
|---|---|---|
| 返回值 | `APIResponse` 对象 | Dict |
| 占位符 | 无 | `${entity.id}` |
| Allure 集成 | 有 | 有 |
| 重试 | 有 | 有 |

BDD APIClient 是 core APIClient 的 BDD 适配层。如果不需要 Dict 返回和占位符，直接使用 core APIClient 即可。
