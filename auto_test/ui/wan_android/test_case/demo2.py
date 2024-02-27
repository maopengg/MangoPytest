from playwright.sync_api import Playwright, sync_playwright, expect
import time

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False, executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://172.16.90.176:8088/portal/")
    page.get_by_placeholder("用户名").click()
    page.get_by_placeholder("用户名").fill("zesk_system")
    page.get_by_placeholder("密码").fill("zesk8888")
    page.get_by_role("button", name="登 录").click()
    time.sleep(3)
    page.frame_locator("iframe").get_by_text("发起流程").click()
    time.sleep(3)
    page.frame_locator("iframe").frame_locator("iframe[name=\"dataFrame\"]").frame_locator("iframe[name=\"Start_Process_Page_0\"]").get_by_text("销售类合同审批", exact=True).click()
    page.frame_locator("iframe").frame_locator("iframe[name=\"dataFrame\"]").frame_locator("iframe[name=\"eaf30ddc-3032-45c7-882b-596db6ba5f8e\"]").get_by_text("主合同-广告销售合同审批单", exact=True).click()
    time.sleep(13)
    page.frame_locator("iframe").frame_locator("iframe[name=\"dataFrame\"]").frame_locator("iframe[name=\"formFrame\"]").get_by_label("合同主体", exact=True).get_by_text("").click()
    page.frame_locator("iframe").frame_locator("iframe[name=\"dataFrame\"]").frame_locator("iframe[name=\"formFrame\"]").get_by_role("row", name="上海相宜本草化妆品股份有限公司 直客").locator("span").nth(1).click()
    page.frame_locator("iframe").frame_locator("iframe[name=\"dataFrame\"]").frame_locator("iframe[name=\"formFrame\"]").get_by_role("button", name="确定").click()
    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
