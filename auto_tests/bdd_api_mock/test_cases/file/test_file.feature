# language: zh-CN
# -*- coding: utf-8 -*-
功能: 文件管理
作为系统用户
我希望能够上传和下载文件
以便管理文件资源

背景:
假如 用户"testuser"已登录

@smoke @positive
场景: 获取服务器信息
当 GET "/info"
那么 响应状态码应该为 200
而且 响应数据应该包含字段 "app_name"
