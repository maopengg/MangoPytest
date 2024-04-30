import pytest
from playwright.sync_api import Page, expect
from playwright.sync_api import sync_playwright


@pytest.fixture(scope='function')
def setup_context_page():
    with sync_playwright as p:
        browser = p.chromium.launch(headless=False,
                                    executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
        page = browser.new_page()
        return page


def test_example(page: Page) -> None:
    page.goto("https://www.baidu.com/")
    page.get_by_role("link", name="登录").click()
    page.get_by_placeholder("手机号/用户名/邮箱").click()
    page.get_by_placeholder("手机号/用户名/邮箱").fill("18311527751")
    page.get_by_text(
        "扫码登录账号登录短信登录验证即登录，未注册将自动创建百度账号发送验证码收不到短信验证码?物联网卡手机号未修改，被限制登录去解禁您账号存在安全风险被限制登录去解禁").click()
    page.get_by_text("扫码登录账号登录短信登录").click()
    page.get_by_placeholder("请输入手机号").click()
    page.get_by_placeholder("请输入手机号").fill("18311527751")
    page.get_by_role("textbox", name="验证码").click()
    page.get_by_role("textbox", name="验证码").click()
    page.get_by_role("checkbox", name="阅读并接受").check()
    page.get_by_role("textbox", name="验证码").click()
    page.get_by_role("textbox", name="验证码").click()
    page.get_by_role("button", name="发送验证码").click()
    page.get_by_role("textbox", name="验证码").click()
    page.get_by_role("textbox", name="验证码").click()
    page.get_by_role("textbox", name="验证码").fill("969439")
    page.get_by_role("button", name="登录").click()
    expect(page.locator("#su")).to_contain_text("百度一下")
