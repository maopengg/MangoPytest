# language: zh-CN
# -*- coding: utf-8 -*-
功能: 文件管理
  作为系统用户
  我希望能够上传和下载文件
  以便管理文件资源

  背景:
    假如 用户"testuser"已登录

  @smoke @positive
  场景: 上传文件成功
    当 上传文件 "data/uploads/测试上传文件.txt" 到 "/upload"
    那么 响应状态码应该为 200
    而且 响应数据应该包含字段 "file_id"

  @smoke @positive
  场景: 下载Excel文件成功
    当 GET "/download/excel"
    那么 响应状态码应该为 200
    而且 下载CSV文件应该包含3列5行数据

  @negative
  场景: 未选择文件上传
    当 POST "/upload" 预期失败
    那么 响应状态码应该为 422

  @positive
  场景: 上传不同格式文件
    当 上传文件 "data/uploads/test.json" 到 "/upload"
    那么 响应状态码应该为 200
    当 上传文件 "data/uploads/test.png" 到 "/upload"
    那么 响应状态码应该为 200
    当 上传文件 "data/uploads/test.xlsx" 到 "/upload"
    那么 响应状态码应该为 200
