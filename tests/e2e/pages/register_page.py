class RegisterPage:
    PATH = "/register.html"

    def __init__(self, page):
        self.page = page

    def goto(self):
        self.page.goto(self.PATH)

    @property
    def email_input(self):
        return self.page.get_by_test_id("register-username")

    @property
    def password_input(self):
        return self.page.get_by_test_id("register-password")

    @property
    def confirm_password_input(self):
        return self.page.get_by_test_id("register-confirm-password")

    @property
    def toggle_password(self):
        return self.page.get_by_test_id("toggle-password")

    @property
    def toggle_confirm_password(self):
        return self.page.get_by_test_id("toggle-confirm-password")

    @property
    def submit_btn(self):
        return self.page.get_by_test_id("register-btn")

    @property
    def email_error(self):
        return self.page.get_by_test_id("register-username-error")

    @property
    def password_error(self):
        return self.page.get_by_test_id("register-password-error")

    @property
    def confirm_password_error(self):
        return self.page.get_by_test_id("register-confirm-password-error")

    @property
    def error_message(self):
        return self.page.get_by_test_id("error-msg")

    @property
    def login_link(self):
        return self.page.get_by_test_id("go-login-link")

    def fill(self, email, password, confirm_password=None):
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.confirm_password_input.fill(
            password if confirm_password is None else confirm_password
        )

    def submit(self):
        self.submit_btn.click()

    def register(self, email, password, confirm_password=None):
        self.goto()
        self.fill(email, password, confirm_password)
        self.submit()
