"""核对另一仓库的公共维护文件；业务差异只允许出现在明确的资产边界内。"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


BUSINESS_FILES = {"README.md"}  # 仓库身份与各自业务的使用说明。
BUSINESS_DIRECTORIES = (
    "auto_tests/",  # 项目、注册表、业务代码、数据和业务维护资料。
    "core/sources/workbooks/",  # 按产品维护的 UI 元素资产。
    "docs/assets/test-cases/",  # 各被测产品的维护用例表。
)


def framework_files(root: Path) -> dict[str, str]:
    output = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
    )
    files = {}
    for raw in output.split(b"\0"):
        if not raw:
            continue
        name = raw.decode("utf-8")
        if name in BUSINESS_FILES or name.startswith(BUSINESS_DIRECTORIES):
            continue
        path = root / name
        if path.is_file():
            files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", required=True, type=Path, help="开源或待比对仓库路径")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    upstream = args.upstream.expanduser().resolve()
    local, other = framework_files(root), framework_files(upstream)
    result = {
        "local": str(root),
        "upstream": str(upstream),
        "compared_files": len(local.keys() | other.keys()),
        "local_only": sorted(local.keys() - other.keys()),
        "upstream_only": sorted(other.keys() - local.keys()),
        "different": sorted(name for name in local.keys() & other.keys() if local[name] != other[name]),
        "business_boundaries": sorted(BUSINESS_FILES) + list(BUSINESS_DIRECTORIES),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(any(result[key] for key in ("local_only", "upstream_only", "different")))


if __name__ == "__main__":
    raise SystemExit(main())
