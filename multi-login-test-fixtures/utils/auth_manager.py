from pathlib import Path
from playwright.sync_api import sync_playwright
from config.settings import BASE_URL, AUTH_STATE_DIR, USERS
from pages.login_page import LoginPage

AUTH_DIR = Path(AUTH_STATE_DIR)


def get_auth_file(role):
    return AUTH_DIR / f"{role}.json"


def create_auth_state(role):
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    auth_file = get_auth_file(role)
    user = USERS[role]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        login_page = LoginPage(page)
        login_page.open(BASE_URL)
        login_page.login(user["username"], user["password"])
        login_page.wait_for_login_success()

        context.storage_state(path=str(auth_file))
        browser.close()


def ensure_auth_state(role):
    auth_file = get_auth_file(role)

    if not auth_file.exists():
        create_auth_state(role)

    return str(auth_file)


def ensure_all_auth_states():
    for role in USERS.keys():
        ensure_auth_state(role)
