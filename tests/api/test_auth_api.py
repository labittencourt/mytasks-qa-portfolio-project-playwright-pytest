"""API tests for /api/auth (register and login).

The scenarios combine:
- Equivalence partitioning and boundary analysis (Bolton/Bach) for the
  email and password fields, since they are the resource's only inputs.
- Consistency oracle (rules described in the README must match the API's
  actual behavior).
- Security "claim" oracle: error messages must not reveal whether an
  email is registered or not.
"""

import pytest

from conftest import DEFAULT_PASSWORD, VALID_EMAIL

pytestmark = pytest.mark.api


class TestRegister:
    @pytest.mark.smoke
    def test_register_with_valid_email_and_password_returns_token(self, api_client, new_user):
        res = api_client.register(new_user["email"], new_user["password"])

        assert res.status_code == 201
        body = res.json()
        assert body["username"] == new_user["email"]
        assert body["token"]

    def test_register_with_duplicate_email_returns_conflict(self, api_client, registered_user):
        res = api_client.register(registered_user["email"], registered_user["password"])

        assert res.status_code == 409
        assert res.json()["error"] == "User already exists"

    @pytest.mark.parametrize(
        "email",
        [
            "no-at-sign.com",
            "no-domain@",
            "@no-user.com",
            "with space@test.com",
            "",
        ],
        ids=["no_at_sign", "no_domain", "no_user", "with_space", "empty"],
    )
    def test_register_with_invalid_email_format_is_rejected(self, api_client, email):
        res = api_client.register(email, DEFAULT_PASSWORD)

        assert res.status_code == 400

    @pytest.mark.parametrize(
        "password",
        [
            "abc12",
            "abcdefgh",
            "12345678",
            "abc123!@",
        ],
        ids=["less_than_6_chars", "no_number", "no_letter", "special_character"],
    )
    def test_register_with_invalid_password_is_rejected(self, api_client, new_user, password):
        res = api_client.register(new_user["email"], password)

        assert res.status_code == 400
        assert "password" in res.json()["error"].lower()

    def test_register_with_minimum_valid_password_length_is_accepted(self, api_client, new_user):
        """Boundary: 6 alphanumeric characters with a letter and a number is the minimum accepted."""
        res = api_client.register(new_user["email"], "abc123")

        assert res.status_code == 201

    @pytest.mark.parametrize(
        "payload",
        [
            {"password": DEFAULT_PASSWORD},
            {"username": VALID_EMAIL},
            {},
        ],
        ids=["missing_username", "missing_password", "empty_payload"],
    )
    def test_register_with_missing_fields_returns_bad_request(self, api_client, payload):
        res = api_client.post("/api/auth/register", json=payload)

        assert res.status_code == 400
        assert res.json()["error"] == "Email and password are required"


class TestLogin:
    @pytest.mark.smoke
    def test_login_with_valid_credentials_returns_token(self, api_client, registered_user):
        res = api_client.login(registered_user["email"], registered_user["password"])

        assert res.status_code == 200
        body = res.json()
        assert body["username"] == registered_user["email"]
        assert body["token"]

    def test_login_with_wrong_password_returns_unauthorized(self, api_client, registered_user):
        res = api_client.login(registered_user["email"], "OtherPassword1")

        assert res.status_code == 401
        assert res.json()["error"] == "Invalid username or password"

    def test_login_with_unknown_email_returns_same_generic_error(self, api_client, new_user):
        """Consistency/security: the message must not reveal whether the email exists."""
        res_unknown = api_client.login(new_user["email"], new_user["password"])

        assert res_unknown.status_code == 401
        assert res_unknown.json()["error"] == "Invalid username or password"

    def test_login_with_invalid_email_format_returns_bad_request(self, api_client):
        res = api_client.login("not-an-email", DEFAULT_PASSWORD)

        assert res.status_code == 400
        assert res.json()["error"] == "Please enter a valid email"

    @pytest.mark.parametrize(
        "payload",
        [
            {"password": DEFAULT_PASSWORD},
            {"username": VALID_EMAIL},
            {},
        ],
        ids=["missing_username", "missing_password", "empty_payload"],
    )
    def test_login_with_missing_fields_returns_bad_request(self, api_client, payload):
        res = api_client.post("/api/auth/login", json=payload)

        assert res.status_code == 400
        assert res.json()["error"] == "Email and password are required"


@pytest.mark.smoke
@pytest.mark.wip
def test_health_check_returns_ok(api_client):
    res = api_client.health()

    assert res.status_code == 200
    assert res.json()["status"] == "ok"
