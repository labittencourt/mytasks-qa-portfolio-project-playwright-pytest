"""E2E tests for the registration screen.

Heuristics applied (Bolton/Bach):
- Consistency with "history": after registering, the user should be taken
  to the login screen (and not logged in automatically) — behavior fixed
  previously and protected here against regression.
- Equivalence partitioning for the email/password/confirmation fields.
"""

import pytest
from playwright.sync_api import expect

from pages.register_page import RegisterPage

pytestmark = pytest.mark.e2e


class TestRegisterForm:
    def test_submit_button_is_disabled_until_inputs_are_valid(self, page):
        register = RegisterPage(page)
        register.goto()

        expect(register.submit_btn).to_be_disabled()

        register.email_input.fill("user@test.com")
        register.password_input.fill("Password123")
        register.confirm_password_input.fill("Password999")
        expect(register.submit_btn).to_be_disabled()

        register.confirm_password_input.fill("Password123")
        expect(register.submit_btn).to_be_enabled()

    def test_invalid_email_format_shows_field_error(self, page):
        register = RegisterPage(page)
        register.goto()
        register.email_input.fill("invalid-user")
        register.password_input.fill("Password123")
        register.confirm_password_input.fill("Password123")
        register.confirm_password_input.press("Enter")

        expect(register.email_error).to_have_text("Please enter a valid email.")

    def test_invalid_password_format_shows_field_error(self, page):
        register = RegisterPage(page)
        register.goto()
        register.email_input.fill("user@test.com")
        register.password_input.fill("nonumbers")
        register.confirm_password_input.fill("nonumbers")
        register.confirm_password_input.press("Enter")

        expect(register.password_error).to_have_text(
            "Password must be at least 6 characters, with letters and numbers."
        )

    def test_password_mismatch_shows_field_error(self, page):
        register = RegisterPage(page)
        register.goto()
        register.email_input.fill("user@test.com")
        register.password_input.fill("Password123")
        register.confirm_password_input.fill("Password999")
        register.confirm_password_input.press("Enter")

        expect(register.confirm_password_error).to_have_text("Passwords do not match.")

    def test_successful_registration_redirects_to_login_with_success_message(self, page, base_url, new_user):
        register = RegisterPage(page)
        register.register(new_user["email"], new_user["password"])

        expect(page).to_have_url(f"{base_url}/login.html?registered=1")
        expect(page.get_by_test_id("success-msg")).to_have_text(
            "Registration successful! Please log in to continue."
        )

    def test_registration_does_not_log_the_user_in_automatically(self, page, base_url, new_user):
        """Previous defect: registering should not create a session or go straight to the home page."""
        register = RegisterPage(page)
        register.register(new_user["email"], new_user["password"])

        expect(page).to_have_url(f"{base_url}/login.html?registered=1")

        session_token = page.evaluate("() => localStorage.getItem('todo_token')")
        assert session_token is None

    def test_duplicate_email_shows_server_error(self, page, registered_user):
        register = RegisterPage(page)
        register.register(registered_user["email"], registered_user["password"])

        expect(register.error_message).to_have_text("User already exists")

    def test_password_visibility_toggle_for_both_fields(self, page):
        register = RegisterPage(page)
        register.goto()
        register.password_input.fill("Password123")
        register.confirm_password_input.fill("Password123")

        expect(register.password_input).to_have_attribute("type", "password")
        expect(register.confirm_password_input).to_have_attribute("type", "password")

        register.toggle_password.click()
        register.toggle_confirm_password.click()

        expect(register.password_input).to_have_attribute("type", "text")
        expect(register.confirm_password_input).to_have_attribute("type", "text")

    def test_login_link_navigates_to_login_page(self, page, base_url):
        register = RegisterPage(page)
        register.goto()
        register.login_link.click()

        expect(page).to_have_url(f"{base_url}/login.html")
