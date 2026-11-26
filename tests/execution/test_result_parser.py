from pathlib import Path

from core.execution.result_parser import parse_failures, parse_junit, status_from_exit_code


def test_junit_parser_and_exit_status(tmp_path: Path) -> None:
    report = tmp_path / "junit.xml"
    report.write_text('<testsuites><testsuite tests="5" failures="1" errors="1" skipped="1"/></testsuites>')
    assert parse_junit(report) == {"total": 5, "passed": 2, "failed": 1, "errors": 1, "skipped": 1}
    assert status_from_exit_code(0).value == "passed"
    assert status_from_exit_code(5).value == "error"


def test_junit_failure_details(tmp_path: Path) -> None:
    report = tmp_path / "junit.xml"
    report.write_text(
        '<testsuite tests="1" failures="1"><testcase classname="tests.auth" name="test_login">'
        '<failure message="expected 200">assert 500 == 200</failure></testcase></testsuite>',
        encoding="utf-8",
    )
    assert parse_failures(report) == [{
        "name": "test_login", "classname": "tests.auth",
        "message": "expected 200", "traceback": "assert 500 == 200",
    }]
