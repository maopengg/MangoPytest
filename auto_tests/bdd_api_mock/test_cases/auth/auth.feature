# language: zh-CN
# -*- coding: utf-8 -*-
功能: 用户认证
作为系统用户
我希望能够登录系统
以便访问受保护的资源

@smoke @positive
场景: 使用正确凭据登录成功
当 用户使用用户名"testuser"和密码"password123"登录
那么 登录应该成功

@smoke @positive
场景: 使用普通用户登录成功
当 用户使用用户名"testuser"和密码"password123"登录
那么 登录应该成功

@negative
场景: 使用错误密码登录失败
当 用户使用用户名"testuser"和密码"wrongpassword"登录
那么 登录应该失败
而且 应该返回错误码 402

@negative
场景: 使用不存在用户登录失败
当 用户使用用户名"nonexistent"和密码"password123"登录
那么 登录应该失败
而且 应该返回错误码 401
