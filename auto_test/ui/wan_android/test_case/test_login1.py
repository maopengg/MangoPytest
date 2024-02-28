# test_example.py
import pytest
from auto_test.ui import browser, page


class TestLogin:

    def test_case_1(self, page):
        page.goto("https://www.example.com")
        assert page.title() == "Example Domain"

    def test_case_2(self, page):
        page.goto("https://www.google.com")
        assert "Google" in page.title()


if __name__ == '__main__':
    pytest.main(['-v', 'test_login1.py'])
