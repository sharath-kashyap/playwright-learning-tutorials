from config.settings import BASE_URL


def test_request_approval_workflow(user_page, manager_page, admin_page):
    user_page.goto(f"{BASE_URL}/requests")
    user_page.click("button:has-text('New Request')")
    user_page.fill("#request-name", "Laptop Request")
    user_page.click("button:has-text('Submit')")
    assert user_page.locator("text=Request submitted").is_visible()

    manager_page.goto(f"{BASE_URL}/approvals")
    manager_page.click("text=Laptop Request")
    manager_page.click("button:has-text('Approve')")
    assert manager_page.locator("text=Approved").is_visible()

    admin_page.goto(f"{BASE_URL}/admin/audit-logs")
    assert admin_page.locator("text=Laptop Request").is_visible()
    assert admin_page.locator("text=Approved by manager").is_visible()
