"""E2E tests for session/logout.

Heuristic applied (Bolton/Bach): historical consistency — after logout,
the application state must return to "unauthenticated" on any protected
route, without leaving session residue.
"""

import pytest
from playwright.sync_api import expect

from pages.todos_page import TodosPage

pytestmark = pytest.mark.e2e


def test_logout_clears_session_and_redirects_to_login(authenticated_page, base_url):
    todos = TodosPage(authenticated_page)

    todos.logout_btn.click()

    expect(authenticated_page).to_have_url(f"{base_url}/login.html")

    token = authenticated_page.evaluate("() => localStorage.getItem('todo_token')")
    assert token is None


def test_protected_page_is_unreachable_after_logout(authenticated_page, base_url):
    todos = TodosPage(authenticated_page)
    todos.logout_btn.click()

    authenticated_page.goto("/index.html")

    expect(authenticated_page).to_have_url(f"{base_url}/login.html")
