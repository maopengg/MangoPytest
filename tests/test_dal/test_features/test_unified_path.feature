# language: zh-CN
功能: 紧凑路径断言 — "{path}"应该为...

  背景:
    假如 准备数据:
      """
      {"name": "张三", "age": 25, "active": true, "deleted": false,
       "address": {"city": "北京", "zip": "100000"},
       "tags": ["VIP", "认证"],
       "items": [{"id": 1}, {"id": 2}, {"id": 3}]}
      """

  场景: 字符串等值
    那么 "name"应该为"张三"

  场景: 整数等值
    那么 "age"应该为25

  场景: 布尔true
    那么 "active"应该为true

  场景: 布尔false
    那么 "deleted"应该为false

  场景: 字段存在
    那么 "address"应该存在

  场景: 嵌套路径
    那么 "address.city"应该为"北京"

  场景: 非空
    那么 "items"不应该为空

  场景: 大小等于
    那么 "items"大小应该为3

  场景: 大小大于
    那么 "items"大小应该大于0

  场景: 包含
    那么 "tags"应该包含"VIP"

  场景: 大于
    那么 "age"应该大于18

  场景: 正则匹配
    那么 "address.zip"应该匹配"\d{6}"
