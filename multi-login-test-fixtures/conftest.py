import pytest
from playwright.sync_api import sync_playwright
from utils.auth_manager import ensure_all_auth_states, ensure_auth_state


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance):
    browser = playwright_instance.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture(scope="session", autouse=True)
def setup_auth_states():
    ensure_all_auth_states()


@pytest.fixture(scope="function")
def admin_context(browser):
    auth_file = ensure_auth_state("admin")
    context = browser.new_context(storage_state=auth_file)
    yield context
    context.close()


@pytest.fixture(scope="function")
def admin_page(admin_context):
    page = admin_context.new_page()
    yield page
    page.close()


@pytest.fixture(scope="function")
def user_context(browser):
    auth_file = ensure_auth_state("user")
    context = browser.new_context(storage_state=auth_file)
    yield context
    context.close()


@pytest.fixture(scope="function")
def user_page(user_context):
    page = user_context.new_page()
    yield page
    page.close()


@pytest.fixture(scope="function")
def manager_context(browser):
    auth_file = ensure_auth_state("manager")
    context = browser.new_context(storage_state=auth_file)
    yield context
    context.close()


@pytest.fixture(scope="function")
def manager_page(manager_context):
    page = manager_context.new_page()
    yield page
    page.close()
