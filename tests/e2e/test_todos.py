"""E2E tests for the task list (authenticated area).

The session is set up via API (`authenticated_page`), and the UI is what's
under test — separation of concerns: fast setup via API, verification
through the interface.

Heuristics applied (Bolton/Bach):
- Product-to-product consistency: the counter must always reflect the
  actual state of the list (SFDPOT structure: "Function" and "Data").
- The empty state is an edge case explicitly handled by the application
  and, therefore, also by the tests.
"""

import pytest
from playwright.sync_api import expect

from pages.todos_page import TodosPage

pytestmark = pytest.mark.e2e


@pytest.fixture
def todos(authenticated_page):
    return TodosPage(authenticated_page)


def test_new_user_sees_empty_state(todos):
    expect(todos.list).to_contain_text("No tasks found.")
    expect(todos.counter).to_have_text("0 task(s) — 0 pending, 0 completed")


def test_create_todo_adds_item_and_updates_counter(todos):
    todos.add_todo("Write automated tests")

    expect(todos.list).to_contain_text("Write automated tests")
    expect(todos.counter).to_have_text("1 task(s) — 1 pending, 0 completed")


def test_create_todo_with_empty_title_shows_error_and_does_not_add_item(todos):
    todos.add_todo("")

    expect(todos.error_message).to_have_text("Title cannot be empty.")
    expect(todos.list).to_contain_text("No tasks found.")


def test_toggle_todo_marks_as_completed_and_updates_counter(todos):
    todos.add_todo("Review PR")

    item = todos.items.first
    todos.checkbox_of(item).check()

    expect(item).to_have_class("todo-item completed")
    expect(todos.counter).to_have_text("1 task(s) — 0 pending, 1 completed")


def test_edit_todo_updates_title(todos):
    todos.add_todo("Original title")

    item = todos.items.first
    todos.edit_button_of(item).click()

    expect(todos.edit_modal).to_be_visible()
    todos.edit_input.fill("Edited title")
    todos.save_edit_btn.click()

    expect(todos.list).to_contain_text("Edited title")
    expect(todos.list).not_to_contain_text("Original title")


def test_cancel_edit_keeps_original_title(todos):
    todos.add_todo("Original title")

    item = todos.items.first
    todos.edit_button_of(item).click()

    expect(todos.edit_modal).to_be_visible()
    todos.edit_input.fill("Title that should not be saved")
    todos.cancel_edit_btn.click()

    expect(todos.edit_modal).to_be_hidden()
    expect(todos.list).to_contain_text("Original title")
    expect(todos.list).not_to_contain_text("Title that should not be saved")


def test_delete_todo_removes_item(todos):
    todos.add_todo("Temporary task")

    item = todos.items.first
    todos.delete_button_of(item).click()

    expect(todos.list).to_contain_text("No tasks found.")


def test_filters_show_correct_subsets(todos):
    todos.add_todo("Pending task")
    expect(todos.list).to_contain_text("Pending task")

    todos.add_todo("Completed task")
    expect(todos.list).to_contain_text("Completed task")

    completed_item = todos.item_by_title("Completed task")
    todos.checkbox_of(completed_item).check()

    todos.filter_btn("active").click()
    expect(todos.list).to_contain_text("Pending task")
    expect(todos.list).not_to_contain_text("Completed task")

    todos.filter_btn("completed").click()
    expect(todos.list).to_contain_text("Completed task")
    expect(todos.list).not_to_contain_text("Pending task")

    todos.filter_btn("all").click()
    expect(todos.list).to_contain_text("Pending task")
    expect(todos.list).to_contain_text("Completed task")
