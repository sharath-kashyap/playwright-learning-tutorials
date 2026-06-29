class LoginPage:
    def __init__(self, page):
        self.page = page

    def open(self, base_url):
        self.page.goto(f"{base_url}/login")

    def login(self, username, password):
        self.page.fill("#username", username)
        self.page.fill("#password", password)
        self.page.click("button[type='submit']")

    def wait_for_login_success(self):
        self.page.wait_for_url("**/dashboard")
