      # language: zh-CN
      # -*- coding: utf-8 -*-
      功能: 用户管理
      作为系统管理员
      我希望能够管理用户
      以便维护系统用户数据

      背景:
      假如 管理员已登录

      @smoke @positive
      场景: 获取所有用户列表
      当 GET "/users"
      那么 响应状态码应该为 200
      而且 响应数据应该是列表
      而且 列表长度应该大于等于 1

      @smoke @positive
      场景: 创建新用户
      假如 存在"用户":
      """
      {
        "username": "AUTO_testuser_new",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "password123"
      }
      """
      那么 数据库中存在"用户"

      @positive
      场景: 根据ID获取指定用户
      假如 存在"用户"
      当 使用用户ID GET "/users?id=${user.id}"
      那么 响应状态码应该为 200
      而且 响应数据应该包含字段 "username"

      @positive
      场景: 更新用户信息
      假如 存在"用户"
      当 使用用户ID PUT "/users/${user.id}":
      """
      {
        "username": "AUTO_updated_user",
        "email": "updated@example.com",
        "full_name": "Updated User",
        "password": "password123"
      }
      """
那么 响应状态码应该为 200
而且 响应数据 "username" 应该为 "AUTO_updated_user"

@positive
场景: 删除用户
假如 存在"用户"
当 使用用户ID DELETE "/users/${user.id}"
那么 响应状态码应该为 200
