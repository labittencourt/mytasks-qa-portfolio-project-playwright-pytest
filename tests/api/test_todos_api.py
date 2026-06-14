"""API tests for /api/todos.

Scenarios prioritized by risk (Bolton): the riskiest function of a
multi-user task list is not the CRUD itself, but the possibility of one
user seeing or changing another's data. That's why `TestDataIsolation`
gets the same attention as the "happy" CRUD flow.
"""

import pytest

pytestmark = pytest.mark.api


class TestAuthorization:
    def test_list_todos_without_token_returns_unauthorized(self, api_client):
        res = api_client.list_todos(token=None)

        assert res.status_code == 401
        assert res.json()["error"] == "Token not provided"

    def test_list_todos_with_malformed_token_returns_unauthorized(self, api_client):
        res = api_client.get("/api/todos", token="invalid-token")

        assert res.status_code == 401
        assert res.json()["error"] == "Invalid or expired token"


class TestCrud:
    @pytest.mark.smoke
    def test_create_list_update_and_delete_todo(self, api_client, registered_user):
        token = registered_user["token"]

        create_res = api_client.create_todo(token, "Write tests")
        assert create_res.status_code == 201
        todo = create_res.json()
        assert todo["title"] == "Write tests"
        assert todo["completed"] == 0

        list_res = api_client.list_todos(token)
        assert any(t["id"] == todo["id"] for t in list_res.json())

        toggle_res = api_client.update_todo(token, todo["id"], completed=True)
        assert toggle_res.status_code == 200
        assert toggle_res.json()["completed"] == 1

        rename_res = api_client.update_todo(token, todo["id"], title="Review tests")
        assert rename_res.status_code == 200
        assert rename_res.json()["title"] == "Review tests"

        delete_res = api_client.delete_todo(token, todo["id"])
        assert delete_res.status_code == 204

        final_list = api_client.list_todos(token).json()
        assert all(t["id"] != todo["id"] for t in final_list)

    @pytest.mark.parametrize("title", ["", "   "], ids=["empty", "only_spaces"])
    def test_create_todo_with_blank_title_is_rejected(self, api_client, registered_user, title):
        res = api_client.create_todo(registered_user["token"], title)

        assert res.status_code == 400
        assert res.json()["error"] == "Title is required"

    def test_update_todo_with_blank_title_is_rejected(self, api_client, registered_user):
        token = registered_user["token"]
        todo = api_client.create_todo(token, "Valid task").json()

        res = api_client.update_todo(token, todo["id"], title="   ")

        assert res.status_code == 400
        assert res.json()["error"] == "Title is required"

    def test_update_nonexistent_todo_returns_not_found(self, api_client, registered_user):
        res = api_client.update_todo(registered_user["token"], 999999, title="x")

        assert res.status_code == 404
        assert res.json()["error"] == "Task not found"

    def test_delete_nonexistent_todo_returns_not_found(self, api_client, registered_user):
        res = api_client.delete_todo(registered_user["token"], 999999)

        assert res.status_code == 404
        assert res.json()["error"] == "Task not found"


class TestDataIsolation:
    """Each user should only see and manipulate their own tasks."""

    def test_new_user_does_not_see_todos_from_other_users(self, api_client, registered_user, second_user):
        api_client.create_todo(registered_user["token"], "Task from user A")

        todos_b = api_client.list_todos(second_user["token"]).json()

        assert todos_b == []

    def test_user_cannot_update_another_users_todo(self, api_client, registered_user, second_user):
        todo = api_client.create_todo(registered_user["token"], "Task from user A").json()

        res = api_client.update_todo(second_user["token"], todo["id"], title="Modified by user B")

        assert res.status_code == 404

    def test_user_cannot_delete_another_users_todo(self, api_client, registered_user, second_user):
        todo = api_client.create_todo(registered_user["token"], "Task from user A").json()

        res = api_client.delete_todo(second_user["token"], todo["id"])
        assert res.status_code == 404

        todos_a = api_client.list_todos(registered_user["token"]).json()
        assert any(t["id"] == todo["id"] for t in todos_a)
