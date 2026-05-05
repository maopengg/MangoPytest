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

@positive
场景: 使用明文密码登录成功
当 用户使用用户名"testuser"和明文密码"password123"登录
那么 登录应该成功

@negative
场景: 使用错误密码登录失败
当 用户使用用户名"testuser"和密码"wrongpassword"登录
那么 登录应该失败
而且 应该返回错误码 402

@negative
场景: 使用不存在用户登录失败
当 用户使用用户名"nonexistentuser"和密码"password123"登录
那么 登录应该失败
而且 应该返回错误码 401

@negative @boundary
场景: 使用空用户名登录失败
当 用户使用空用户名和密码"password123"登录
那么 登录应该失败
而且 应该返回错误码 400

@negative @boundary
场景: 使用空密码登录失败
当 用户使用用户名"testuser"和空密码登录
那么 登录应该失败
而且 应该返回错误码 400

@smoke @positive
场景: 新用户注册成功
当 用户使用随机用户名和密码"password123"注册
那么 注册应该成功

@negative
场景: 使用已存在用户名注册失败
当 用户使用用户名"testuser"和密码"password123"注册
那么 注册应该失败
而且 注册应该返回错误码 400

@negative @boundary
场景: 使用空用户名注册失败
当 用户使用空用户名和密码"password123"注册
那么 注册应该失败
而且 注册应该返回错误码 400

@positive
场景: 使用MD5密码注册成功
当 用户使用MD5密码"482c811da5d5b4bc6d497ffa98491e38"注册
那么 注册应该成功
