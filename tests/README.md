# Automated tests (Pytest + Playwright)

API and end-to-end (E2E) test suite written in Python, without BDD/Gherkin
— just `pytest` functions and classes, organized by layer.

## Structure

```
tests/
├── conftest.py          # shared fixtures (base_url, api_client, users, session)
├── pytest.ini
├── requirements.txt
├── utils/
│   └── api_client.py    # thin HTTP client for the backend API
├── api/                  # API tests (backend), no browser
│   ├── test_auth_api.py
│   └── test_todos_api.py
└── e2e/                  # end-to-end tests (frontend), via Playwright
    ├── pages/            # Page Objects (LoginPage, RegisterPage, TodosPage)
    ├── test_login.py
    ├── test_register.py
    ├── test_todos.py
    └── test_session.py
```

## How to run

### Via Docker Compose (recommended)

With `backend` and `frontend` already running (`docker compose up --build -d`):

```bash
docker compose --profile test up tests
```

The HTML report is generated at `tests/playwright-report/index.html` and the
JUnit result at `tests/junit.xml` (both ignored by Git).

### Locally

```bash
cd tests
pip install -r requirements.txt
playwright install chromium

# optional variables (defaults below already assume the app is running locally)
export BASE_URL=http://localhost      # frontend
export API_URL=http://localhost:3001  # backend

pytest                         # everything (runs in parallel, see below)
pytest -m api                  # API only
pytest -m e2e                  # E2E only
pytest -m e2e --headed         # E2E with visible browser
pytest -n 0                    # disable parallelism, run sequentially
pytest -m smoke                # critical regression subset (fast)
pytest -m wip                  # only tests marked @pytest.mark.wip
```

## Test strategy

The scenarios were designed based on testing heuristics popularized by
Michael Bolton and James Bach (Rapid Software Testing), rather than from
user stories in Given/When/Then format:

- **Consistency oracles (part of FEW HICCUPPS)**
  - *Internal product consistency*: the task counter, filters and list must
    always agree with each other (`test_todos.py`).
  - *Consistency with history*: previously fixed behaviors — registration
    doesn't log the user in automatically, logout clears the session —
    received dedicated regression tests.
  - *Consistency with the user's image/expectation*: error messages appear
    next to the right field, in red, and action buttons only enable with
    valid data.
  - *"Claim vs. implementation" consistency*: the email/password rules
    described to the user are verified both in the API and the UI.

- **Equivalence partitioning and boundary analysis**
  Used for the email and password fields (`test_auth_api.py`,
  `test_login.py`, `test_register.py`): valid/invalid email formats,
  password at the minimum 6-character limit, missing letter/number, etc.

- **Risk-based testing**
  Data isolation between users (`TestDataIsolation` in
  `test_todos_api.py`) gets the same weight as the "happy" CRUD flow, since
  it's the scenario whose failure would have the greatest impact (data
  leakage between accounts).

- **Setup via API, verification via UI**
  E2E tests that aren't about login/registration use the
  `authenticated_page` fixture, which creates the user via API and injects
  the session via `localStorage`. This avoids repeating the login flow in
  every scenario and reduces flakiness, keeping the test focused on the
  behavior under examination.

## Best practices applied

- **Page Object Model** for E2E tests (`e2e/pages/`), isolating
  locators from test logic.
- **Per-test isolated data**: each test creates its own user with a
  unique email (`uuid4`), avoiding dependence on execution order.
- **`api` / `e2e` markers** to run subsets of the suite.
- **Reusable API client** (`utils/api_client.py`) instead of `requests`
  calls scattered across the tests.
- **Parallel execution** via `pytest-xdist` (`-n auto` in `pytest.ini`,
  one worker per CPU core). This is only safe because every test
  creates its own user with a unique email (`new_user`,
  `registered_user`, `second_user`), so workers never share or fight
  over the same rows. Use `pytest -n 0` to fall back to sequential
  execution (e.g. for debugging or to get strictly ordered output).

## Test markers

Registered in `pytest.ini`:

- **`api`** — all tests under `api/` (no browser).
- **`e2e`** — all tests under `e2e/` (Playwright).
- **`smoke`** — the critical regression subset: one happy-path test per
  major feature, kept small so it runs fast and catches major
  breakages. Run with `pytest -m smoke`. Currently covers:
  - `test_health_check_returns_ok` — backend is up (`api/test_auth_api.py`)
  - `test_register_with_valid_email_and_password_returns_token` — register via API
  - `test_login_with_valid_credentials_returns_token` — login via API
  - `test_create_list_update_and_delete_todo` — full task CRUD via API
  - `test_successful_login_redirects_to_home_and_shows_user_email` — login via UI
  - `test_successful_registration_redirects_to_login_with_success_message` — register via UI
  - `test_create_todo_adds_item_and_updates_counter` — create task via UI
  - `test_toggle_todo_marks_as_completed_and_updates_counter` — complete task via UI
  - `test_edit_todo_updates_title` — edit task via UI
  - `test_delete_todo_removes_item` — delete task via UI
  - `test_logout_clears_session_and_redirects_to_login` — logout via UI

  Field validation, boundary cases, data isolation and other edge
  cases are deliberately left out of `smoke` — they're covered by the
  full suite (`pytest`).

- **`wip`** — work in progress, see below.

### `wip`: working on a single test

While working on a specific test, mark it with `@pytest.mark.wip` and run
`pytest -m wip` to execute only that test (no need to remember its full
path/name). The marker is meant to be temporary — **remove it before
committing**.

At the time of writing, the following tests carry `@pytest.mark.wip`
(remove once the related work is finished):
- `test_health_check_returns_ok` (`api/test_auth_api.py`)
- `test_create_todo_adds_item_and_updates_counter` (`e2e/test_todos.py`)

## Locator strategies

`data-testid` works everywhere, but relying on it exclusively hides
real accessibility/usability problems and doesn't reflect how a real
QA suite is usually written. The page objects intentionally mix
several Playwright locator strategies, each chosen for what it best
demonstrates or verifies:

- **`get_by_placeholder`** — `LoginPage.email_input` /
  `password_input`, `TodosPage.input`. Ties the test to the text the
  *user* sees in the field, so it also acts as a (light) check that
  the placeholder copy didn't regress.

- **`get_by_role` (with accessible name)** — `LoginPage.submit_btn`
  (`button "Login"`), `register_link` (`link "Register"`),
  `TodosPage.add_btn`, `logout_btn`, `save_edit_btn`,
  `cancel_edit_btn`, and the per-item `edit_button_of` /
  `delete_button_of`. Exercises the ARIA role tree (`button`, `link`,
  `list`, `listitem`, `checkbox`, `textbox` via implicit roles on
  `<ul>`, `<li>`, `<input>`, `<button>`, `<a>`), which doubles as a
  basic accessibility smoke check — if a button loses its accessible
  name, these locators fail too.

- **CSS id selectors (`#id`)** — `LoginPage.email_error`,
  `password_error`, `toggle_password`; `TodosPage.error_message`,
  `counter`, `user_label`, `edit_modal`. Used for elements identified
  primarily by a unique DOM id rather than visible text (error
  messages, counters, containers).

  - `toggle_password` is a deliberate exception to the
    "prefer accessible name" rule above: `auth.js` toggles its
    `aria-label` between *"Show password"* and *"Hide password"* on
    each click, so a role+name locator would stop matching after the
    first click. The stable CSS id is the right tool here.

- **CSS class selectors (`.class`)** — `LoginPage.error_message`
  (`.error-msg`), `TodosPage.items` (`.todo-item`). Matches elements
  that are styled/identified as a group rather than individually.

- **CSS attribute selectors** — `TodosPage.filter_btn(name)` builds
  `button.filter-btn[data-filter='{name}']`, combining a class with a
  data attribute to pick one of several visually similar filter
  buttons.

- **`get_by_test_id`** — `LoginPage.success_message`,
  `TodosPage.item_by_id`, and the entirety of `RegisterPage`. Kept for
  elements with no stable text/role/id of their own (e.g. dynamically
  rendered success banners) and to keep one page object as a reference
  example of a pure test-id-based POM.

- **Chained / scoped locators** — `TodosPage.edit_input`,
  `save_edit_btn`, `cancel_edit_btn` are all resolved from
  `edit_modal.get_by_role(...)`, scoping the search to inside the
  modal so they can't accidentally match a similarly-named element
  elsewhere on the page. Likewise `items` is `list.locator(".todo-item")`.

- **Locator filtering** — `TodosPage.item_by_title(title)` uses
  `.filter(has_text=title)` to find a specific row by its visible
  text; `item_by_id(todo_id)` uses
  `.filter(has=page.get_by_test_id(f"checkbox-{todo_id}"))` to find a
  row that *contains* a given child locator. Both build on `items`
  (a chained locator) and demonstrate two different ways to pick one
  element out of a repeated list without relying on index.

- **Function-based / parameterized locators** — `filter_btn(name)`,
  `item_by_title(title)`, `item_by_id(todo_id)`,
  `checkbox_of(item)`, `edit_button_of(item)`,
  `delete_button_of(item)` are all methods rather than fixed
  properties: they take the variable part (a name, a title, an id, or
  a parent item) as an argument and return a freshly scoped locator,
  avoiding one property per dynamic row/button.
