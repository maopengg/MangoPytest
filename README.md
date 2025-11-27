# MangoPytest

<p align="center">
  <img src="img_8.png" alt="Logo" width="200">
</p>

#### 介绍

MangoPytest 是一个集UI+API自动化于一体的自动化测试平台，支持多项目多产品的测试需求！测试数据管理提供3种方式，分别是：SQLite、Excel 和飞书共享文档。可以通过飞书共享文档管理测试用例、测试数据和项目数据，方便团队协作完成自动化任务。

对于自动化编写，采用手动编写测试用例、接口和UI步骤的方式，自定义程度高，可以完成复杂的自动化测试场景。支持对测试环境进行动态管理，通知可以绑定测试项目，将测试结果发送给相关人员进行通知！

#### 核心特性

- ✅ **双重自动化支持**：同时支持API接口测试和UI界面测试
- 📊 **多元化数据管理**：支持SQLite数据库、Excel文件、飞书文档三种数据源
- 👥 **团队协作友好**：基于飞书文档的在线协同编辑，便于团队合作维护测试用例
- 🔧 **高度可定制**：手动编写测试用例，灵活适应各种复杂测试场景
- 📝 **智能通知系统**：测试结果自动通知，支持多种通知渠道
- 🔄 **动态环境管理**：支持多环境切换，灵活配置测试环境
- 📈 **详细测试报告**：集成Allure测试报告，可视化展示测试结果
- 🎯 **精准定位**：支持多种元素定位方式，确保UI测试稳定性

---

#### 安装教程&功能介绍

参照文档进行安装：http://43.142.161.61:8002/pages/mango-pytest/deploy.html

---

## 项目结构

```
MangoPytest/
├── auto_test/              # 自动化测试主目录
│   ├── api_mango_mock/     # API测试项目示例
│   ├── sql_auto/           # SQL测试项目示例
│   ├── ui_baidu/           # UI测试项目示例
│   └── project_config.py   # 项目配置文件
├── enums/                  # 枚举类型定义
├── exceptions/             # 异常处理
├── models/                 # 数据模型定义
├── service/                # 服务层
├── settings/               # 配置文件
├── sources/                # 数据源管理
│   ├── excel/              # Excel数据源
│   ├── feishu/             # 飞书文档数据源
│   └── sql/                # SQL数据源
├── tests/                  # 测试相关文件
└── tools/                  # 工具类
    ├── base_object/        # 基础对象
    ├── base_request/       # 请求基础类
    ├── decorator/          # 装饰器
    └── files/              # 文件处理
```

---

## 快速开始

### 1. 环境准备

确保已安装Python 3.8+，然后安装依赖：

```bash
pip install -r requirements.txt
```

### 2. 配置数据源

在 `settings/settings.py` 中配置数据源类型：

```python
# 数据源选择
SOURCES_TYPE = SourcesTypeEnum.EXCEL  # 可选：EXCEL, DOCUMENT, SQL
```

### 3. 运行测试

执行主程序运行测试：

```bash
python main.py
```

---

## 使用示例

### API测试示例

```python
@allure.epic('演示-API自动化-常规API-玩安卓')
@allure.feature('登录模块')
class TestLogin(LoginAPI, CaseTool):
    test_data: ObtainTestData = ObtainTestData()

    @case_data([1, 2, 3])
    def test_01(self, data: ApiDataModel):
        data = self.api_login(data)
        assert data.response.response_dict.get('message') is not None
```

### UI测试示例

```python
@allure.epic('演示-UI自动化-WEB项目-Gitee')
@allure.feature('搜索自己的开源项目')
class TestOpenSource:
    base_data = base_data
    test_data: ObtainTestData = ObtainTestData()

    @case_data([1, 2])
    def test_01(self, execution_context, data: UiDataModel):
        login_page = HomePage(execution_context, base_data, self.test_data)
        login_page.goto()
        login_page.click_open_source()
        open_source_page = ResultPage(execution_context, base_data, self.test_data)
        open_source_page.search_for_open_source_projects(data.test_case.data.get('name'))
        open_source_page.w_wait_for_timeout(3)
```

---

---

## 数据源管理

### SQLite数据库

适用于本地开发和小型项目，数据存储在本地SQLite文件中。

### Excel文件

适用于简单项目和快速原型开发，通过Excel表格维护测试数据。

### 飞书文档

适用于团队协作项目，支持多人在线编辑测试用例和数据。

---

## 测试报告

项目集成了Allure测试报告框架，提供详细的测试执行信息：
- 执行结果统计
- 失败用例详情
- 执行时间分析
- 图片和日志附件

生成报告命令：
```bash
allure generate ./report/tmp -o ./report/html --clean
allure serve ./report/tmp
```

---

## 贡献指南

欢迎任何形式的贡献！

### 提交Issue

如果您发现了bug或者有功能建议，请提交issue。

### 提交Pull Request

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 社区支持

#### 加作者微信，进芒果自动化测试群(记得备注：MangoPytest。否则可能会不通过哦)

![img_8.png](img_8.png)

---

## 许可证

### 支持

- 运用在自己公司来完成自动化任务
- 学习、交流测试平台

### 不支持

- 收费教学、二次销售、等盈利活动

### 二次开发注意项

- 请遵守AGPL-3.0协议，不支持修改和删除该协议
- 不支持修改包含作者署名版本的内容
- 不支持修改测试平台名称
- 不支持修改和删除README中的作者联系方式
- 不支持修改前端项目和执行器项目中的帮助文档跳转操作

测试git提交：1