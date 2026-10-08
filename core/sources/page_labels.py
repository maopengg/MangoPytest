"""元素表的页面标识到中文页面名的映射。

元素表里的 ``页面名称`` 是稳定的页面键（如 ``componentsPage``），直接作为
``ElementModel.category`` 送进 AI 请求时语义很弱；映射成中文后能让模型更好地
判断"元素是否出现在正确的页面区域"。

本模块刻意不引入任何重型依赖：``core/ui/element_runtime.py`` 会在每次操作时用到它，
不能因此把 openpyxl / pandas 拉进 UI 运行路径。未注册的产品或页面键会原样返回，
保证新增元素产品时不阻塞。
"""

from __future__ import annotations

#: ``项目名称``（元素表的"项目名称"列）→ 页面键 → 中文页面名
PRODUCT_PAGE_LABELS: dict[str, dict[str, str]] = {
    "MockUI服务": {
        "global": "页面全局",
        "scenariosPage": "场景目录页",
        "httpPage": "HTTP API 靶场页",
        "componentsPage": "组件演示页",
        "ssePage": "SSE 事件流页",
        "websocketPage": "WebSocket 靶场页",
        "mcpPage": "MCP 页",
        "grpcPage": "gRPC 页",
    },
}


def page_display_name(product_name: str | None, page_name: str | None) -> str:
    """返回页面键对应的中文页面名；未注册时回退为原页面键。"""

    page = str(page_name or "").strip()
    if not page:
        return ""
    labels = PRODUCT_PAGE_LABELS.get(str(product_name or "").strip(), {})
    return labels.get(page, page)


__all__ = ["PRODUCT_PAGE_LABELS", "page_display_name"]
