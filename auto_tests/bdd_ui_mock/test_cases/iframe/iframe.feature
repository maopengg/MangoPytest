# language: zh-CN
功能: iframe 操作

  背景:
    假如 用户访问 Mock 首页

  @ui @positive
  场景: 操作 iframe 中元素
    当 用户进入 iframe 页面
    而且 用户操作 iframe 中元素
    那么 iframe 操作应该成功
