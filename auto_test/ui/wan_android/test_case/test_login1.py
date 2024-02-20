# test_example.py
import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    return browser.new_page()


def test_case_1(page):
    page.goto("https://www.example.com")
    assert page.title() == "Example Domain"


def test_case_2(page):
    page.goto("https://www.google.com")
    assert "Google" in page.title()


if __name__ == '__main__':
    pytest.main(['-v', 'test_login1.py'])