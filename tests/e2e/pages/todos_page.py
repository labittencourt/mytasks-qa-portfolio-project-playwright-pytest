class TodosPage:
    PATH = "/index.html"

    def __init__(self, page):
        self.page = page

    def goto(self):
        self.page.goto(self.PATH)

    @property
    def input(self):
        return self.page.get_by_placeholder("Enter a new task...")

    @property
    def add_btn(self):
        return self.page.get_by_role("button", name="Add")

    @property
    def error_message(self):
        return self.page.locator("#error-msg")

    @property
    def counter(self):
        return self.page.locator("#counter")

    @property
    def list(self):
        return self.page.get_by_role("list")

    @property
    def items(self):
        return self.list.locator(".todo-item")

    @property
    def user_label(self):
        return self.page.locator("#user-label")

    @property
    def logout_btn(self):
        return self.page.get_by_role("button", name="Logout")

    @property
    def edit_modal(self):
        return self.page.locator("#edit-modal")

    @property
    def edit_input(self):
        return self.edit_modal.get_by_role("textbox")

    @property
    def save_edit_btn(self):
        return self.edit_modal.get_by_role("button", name="Save")

    @property
    def cancel_edit_btn(self):
        return self.edit_modal.get_by_role("button", name="Cancel")

    def add_todo(self, title):
        self.input.fill(title)
        self.add_btn.click()

    def filter_btn(self, name):
        return self.page.locator(f"button.filter-btn[data-filter='{name}']")

    def item_by_title(self, title):
        return self.items.filter(has_text=title)

    def item_by_id(self, todo_id):
        return self.items.filter(has=self.page.get_by_test_id(f"checkbox-{todo_id}"))

    def checkbox_of(self, item):
        return item.get_by_role("checkbox")

    def edit_button_of(self, item):
        return item.get_by_role("button", name="Edit")

    def delete_button_of(self, item):
        return item.get_by_role("button", name="Delete")
