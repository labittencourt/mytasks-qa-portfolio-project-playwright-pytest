import os
import uuid

import pytest

from utils.api_client import ApiClient

DEFAULT_PASSWORD = "Password123"
VALID_EMAIL = "user@test.com"


@pytest.fixture(scope="session")
def base_url():
    """Frontend URL, used by the E2E tests (pytest-playwright)."""
    return os.environ.get("BASE_URL", "http://localhost")


@pytest.fixture(scope="session")
def api_url():
    """Backend base URL, used by the API tests."""
    return os.environ.get("API_URL", "http://localhost:3001")


@pytest.fixture(scope="session")
def api_client(api_url):
    return ApiClient(api_url)


def random_email() -> str:
    return f"qa.{uuid.uuid4().hex[:12]}@test.com"


@pytest.fixture
def new_user():
    """Data for a user that is not yet registered (unique email per test)."""
    return {"email": random_email(), "password": DEFAULT_PASSWORD}


@pytest.fixture
def registered_user(api_client, new_user):
    """Creates a user via API and returns their credentials + token."""
    res = api_client.register(new_user["email"], new_user["password"])
    assert res.status_code == 201, res.text

    return {**new_user, "token": res.json()["token"]}


@pytest.fixture
def second_user(api_client):
    """A second, independent user, used in data isolation tests."""
    email = random_email()
    res = api_client.register(email, DEFAULT_PASSWORD)
    assert res.status_code == 201, res.text

    return {"email": email, "password": DEFAULT_PASSWORD, "token": res.json()["token"]}


@pytest.fixture
def authenticated_page(page, registered_user):
    """Injects a user's session via localStorage.

    Avoids repeating the login flow in tests that aren't about login,
    using the API only to set up state (fast and stable setup).
    """
    page.goto("/login.html")
    page.evaluate(
        "([token, email]) => { "
        "localStorage.setItem('todo_token', token); "
        "localStorage.setItem('todo_username', email); }",
        [registered_user["token"], registered_user["email"]],
    )
    page.goto("/index.html")
    return page
