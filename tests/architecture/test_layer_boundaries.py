"""根 tests/ 必须能同步到任意业务仓库，不直接导入自动化项目。"""

import ast


def test_framework_tests_do_not_import_business_projects(repository_root):
    violations = []
    for path in (repository_root / "tests").rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            modules = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                modules = [node.module or ""]
            elif (
                isinstance(node, ast.Call) and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.func, ast.Name)
                and node.func.id in {"import_module", "__import__"}
            ):
                modules = [node.args[0].value]
            for module in modules:
                if isinstance(module, str) and (
                    module == "auto_tests" or module.startswith("auto_tests.")
                ):
                    violations.append(f"{path.relative_to(repository_root)}:{node.lineno} {module}")
    assert not violations, "业务专属检查应放回 auto_tests/：\n" + "\n".join(violations)


def test_console_layers_keep_http_and_persistence_at_the_boundary(repository_root):
    rules = {
        "api/routes": ("sqlite3", "subprocess", "core.execution.subprocess_runner"),
        "services": ("fastapi", "web_console.api"),
        "repositories": ("fastapi", "web_console.api", "web_console.services"),
        "plugins": ("fastapi", "web_console.api"),
    }
    violations = []
    for directory, forbidden in rules.items():
        for path in (repository_root / "web_console" / directory).rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                modules = []
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    modules = [node.module or ""]
                for module in modules:
                    if any(module == prefix or module.startswith(prefix + ".") for prefix in forbidden):
                        violations.append(f"{path.relative_to(repository_root)}:{node.lineno} {module}")
    assert not violations, "控制台层级依赖越界：\n" + "\n".join(violations)
