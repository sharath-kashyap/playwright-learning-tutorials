
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture
def page_fixture():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        yield page

        page.close()
        context.close()
        browser.close()

def test_example(page_fixture):
    page_fixture.goto("https://www.google.com")
    print(page_fixture.title())
    assert "Google" in page_fixture.title()

if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-s"]))