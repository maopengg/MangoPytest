"""通过 HTTP 读取入口及本地依赖，验证拆分后的静态资源能完整加载。"""

import re
from urllib.parse import urljoin, urlsplit


def contains(source: str, fragment: str) -> bool:
    def compact(value):
        return re.sub(r"\s+", "", value).replace(";}", "}").rstrip(";")
    return compact(fragment) in compact(source)


def read_static_assets(client, entry: str) -> dict[str, str]:
    documents = {}

    def read(url):
        url = urlsplit(url).path
        if url in documents:
            return
        assert url.startswith("/static/"), url
        response = client.get(url)
        assert response.status_code == 200, url
        documents[url] = response.text
        if url.endswith(".js"):
            dependencies = re.findall(r"\bfrom\s+['\"]([^'\"]+)['\"]", response.text)
        else:
            dependencies = re.findall(r"@import\s+url\(['\"]?([^'\")]+)", response.text)
        for dependency in dependencies:
            read(urljoin(url, dependency))

    read(entry)
    return documents
