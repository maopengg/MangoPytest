# language: zh-CN
功能: 浏览器弹窗操作

  背景:
    假如 用户访问 Mock 首页

  @ui @positive
  场景: 触发 alert 弹窗
    当 用户进入浏览器弹窗页面
    而且 用户触发 alert 弹窗
    那么 浏览器弹窗操作应该成功

  @ui @positive
  场景: 触发 confirm 弹窗
    当 用户进入浏览器弹窗页面
    而且 用户触发 confirm 弹窗
    那么 浏览器弹窗操作应该成功

  @ui @positive
  场景: 触发 prompt 弹窗
    当 用户进入浏览器弹窗页面
    而且 用户触发 prompt 弹窗
    那么 浏览器弹窗操作应该成功
