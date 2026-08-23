"""同步 Web Runtime 的兼容关闭逻辑。"""

from playwright.sync_api import Error as PlaywrightError


def close_sync_web_runtime(runtime, log) -> None:
    """停止 Playwright Driver，并由其级联关闭 Browser。

    mangoautomation 2.0.4 的 ``SyncWebRuntime.close`` 当前只关闭 Browser；
    在 xdist Worker 中 ``browser.close`` 可能等待 Driver 而无法退出，因此优先
    使用 Playwright 的完整停止入口。待内部包修复后可删除此兼容逻辑。
    """
    browser_runtime = runtime.browser_runtime
    playwright = getattr(browser_runtime, "playwright", None)
    if playwright is None:
        runtime.close()
        return
    try:
        playwright.stop()
    except PlaywrightError as error:
        log.debug(f"停止 Playwright Driver 时出错: {error}")
    finally:
        browser_runtime.browser = None
        browser_runtime.playwright = None
