class LoginPage:
    PATH = "/login.html"

    def __init__(self, page):
        self.page = page

    def goto(self):
        self.page.goto(self.PATH)

    @property
    def email_input(self):
        return self.page.get_by_placeholder("Email")

    @property
    def password_input(self):
        return self.page.get_by_placeholder("Password")

    @property
    def toggle_password(self):
        return self.page.locator("#toggle-password")

    @property
    def submit_btn(self):
        return self.page.get_by_role("button", name="Login")

    @property
    def email_error(self):
        return self.page.locator("#username-error")

    @property
    def password_error(self):
        return self.page.locator("#password-error")

    @property
    def error_message(self):
        return self.page.locator(".error-msg")

    @property
    def success_message(self):
        return self.page.get_by_test_id("success-msg")

    @property
    def register_link(self):
        return self.page.get_by_role("link", name="Register")

    def fill_credentials(self, email, password):
        self.email_input.fill(email)
        self.password_input.fill(password)

    def submit(self):
        self.submit_btn.click()

    def login(self, email, password):
        self.goto()
        self.fill_credentials(email, password)
        self.submit()
