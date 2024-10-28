import json

import requests
from jsonschema import Draft7Validator

# 发送请求并获取响应
response = requests.get('https://api.example.com/resource')
data = response.json()

# 生成 JSON Schema
validator = Draft7Validator.check_schema(data)
schema = validator.schema

# 保存到 schema.json
with open('schema.json', 'w') as f:
    json.dump(schema, f, indent=2)

# 加载 JSON Schema
with open('schema.json') as f:
    schema = f.read()


def test_api_response():
    # 发送请求
    response = requests.get('https://api.example.com/resource')

    # 验证响应状态码
    assert response.status_code == 200

    # 验证响应 JSON 格式
    validate(instance=response.json(), schema=schema)
