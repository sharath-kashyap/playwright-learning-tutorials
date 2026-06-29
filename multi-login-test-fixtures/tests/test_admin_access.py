from config.settings import BASE_URL


def test_admin_can_open_admin_panel(admin_page):
    admin_page.goto(f"{BASE_URL}/admin")
    assert admin_page.locator("text=Admin Dashboard").is_visible()


def test_user_cannot_open_admin_panel(user_page):
    user_page.goto(f"{BASE_URL}/admin")
    assert user_page.locator("text=Access Denied").is_visible()
