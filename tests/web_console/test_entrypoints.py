"""验证模块和 IDE 文件入口；不实际启动服务或修改运行数据库。"""

import os
import subprocess
import sys

import pytest


@pytest.mark.parametrize("entry", ["module", "file", "file-from-other-directory"])
def test_console_entrypoint_help_without_pythonpath(entry, repository_root, tmp_path):
    target = repository_root / "web_console/app.py"
    arguments = ["-m", "web_console"] if entry == "module" else [str(target)]
    environment = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    result = subprocess.run(
        [sys.executable, *arguments, "--help"],
        cwd=tmp_path if entry == "file-from-other-directory" else repository_root,
        env=environment, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert all(option in result.stdout for option in ("--host", "--port", "--reload"))


def test_direct_file_dispatches_resolvable_factory_and_cli_options(repository_root, tmp_path):
    target = repository_root / "web_console/app.py"
    script = """
import importlib, json, runpy, sys
import uvicorn
target = sys.argv[1]
def capture(application, **options):
    module, name = application.split(':')
    assert callable(getattr(importlib.import_module(module), name))
    print('entrypoint-probe:' + json.dumps({'target': application, **options}))
uvicorn.run = capture
sys.argv = [target, '--host', 'localhost', '--port', '8891', '--reload']
runpy.run_path(target, run_name='__main__')
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(target)], cwd=tmp_path,
        env={key: value for key, value in os.environ.items() if key != "PYTHONPATH"},
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    import json
    line = next(line for line in result.stdout.splitlines() if line.startswith("entrypoint-probe:"))
    assert json.loads(line.removeprefix("entrypoint-probe:")) == {
        "target": "web_console.app:create_app", "factory": True,
        "host": "localhost", "port": 8891, "reload": True,
    }
