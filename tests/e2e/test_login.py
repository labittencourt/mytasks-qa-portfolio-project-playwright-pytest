"""E2E tests for the login screen.

Heuristics applied (Bolton/Bach):
- Product-to-product consistency: what the UI shows must reflect the same
  validation rules applied by the API (email/password).
- Consistency with the "image": invalid fields show feedback next to the
  field, in red, and the main button only enables with valid data.
- Historical consistency: an authenticated user should not see the login
  screen again (and vice versa for a user without a session).
"""

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage

pytestmark = pytest.mark.e2e


def test_unauthenticated_user_is_redirected_to_login(page, base_url):
    page.goto("/")

    expect(page).to_have_url(f"{base_url}/login.html")


class TestLoginForm:
    def test_submit_button_is_disabled_until_inputs_are_valid(self, page):
        login = LoginPage(page)
        login.goto()

        expect(login.submit_btn).to_be_disabled()

        login.fill_credentials("invalid-user", "123")
        expect(login.submit_btn).to_be_disabled()

        login.email_input.fill("user@test.com")
        login.password_input.fill("Password123")
        expect(login.submit_btn).to_be_enabled()

    def test_invalid_email_format_shows_field_error(self, page):
        login = LoginPage(page)
        login.goto()
        login.email_input.fill("invalid-user")
        login.password_input.fill("Password123")
        login.password_input.press("Enter")

        expect(login.email_error).to_have_text("Please enter a valid email.")

    def test_invalid_password_format_shows_field_error(self, page):
        login = LoginPage(page)
        login.goto()
        login.email_input.fill("user@test.com")
        login.password_input.fill("nonumbers")
        login.password_input.press("Enter")

        expect(login.password_error).to_have_text(
            "Password must be at least 6 characters, with letters and numbers."
        )

    def test_unknown_credentials_show_generic_error_message(self, page, new_user):
        login = LoginPage(page)
        login.login(new_user["email"], new_user["password"])

        expect(login.error_message).to_have_text("Invalid username or password")

    def test_successful_login_redirects_to_home_and_shows_user_email(self, page, base_url, registered_user):
        login = LoginPage(page)
        login.login(registered_user["email"], registered_user["password"])

        expect(page).to_have_url(f"{base_url}/index.html")
        expect(page.get_by_test_id("user-label")).to_have_text(registered_user["email"])

    def test_password_visibility_toggle(self, page):
        login = LoginPage(page)
        login.goto()
        login.password_input.fill("Password123")

        expect(login.password_input).to_have_attribute("type", "password")

        login.toggle_password.click()
        expect(login.password_input).to_have_attribute("type", "text")

        login.toggle_password.click()
        expect(login.password_input).to_have_attribute("type", "password")

    def test_register_link_navigates_to_register_page(self, page, base_url):
        login = LoginPage(page)
        login.goto()
        login.register_link.click()

        expect(page).to_have_url(f"{base_url}/register.html")


def test_authenticated_user_visiting_login_is_redirected_home(authenticated_page, base_url):
    authenticated_page.goto("/login.html")

    expect(authenticated_page).to_have_url(f"{base_url}/index.html")
