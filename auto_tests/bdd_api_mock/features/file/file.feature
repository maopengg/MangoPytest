# language: zh-CN
# -*- coding: utf-8 -*-
功能: 文件管理
  作为系统用户
  我希望能够上传和下载文件
  以便管理文件资源

  背景:
    假如 用户"testuser"已登录

  @smoke @positive
  场景: 获取文件列表
    当 GET "/files"
    那么 响应状态码应该为 200
    而且 响应数据应该是列表
