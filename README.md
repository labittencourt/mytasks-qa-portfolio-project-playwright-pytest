# QA Portfolio — Todo List

[![Tests](https://github.com/labittencourt/mytasks-qa-portfolio-project-playwright-pytest/actions/workflows/tests.yml/badge.svg)](https://github.com/labittencourt/mytasks-qa-portfolio-project-playwright-pytest/actions/workflows/tests.yml)

Full-stack Todo List application with authentication, built as a portfolio project for QA/test automation (E2E with Playwright).

## Stack

- **Backend**: Node.js + Express + SQLite (`better-sqlite3`), JWT authentication
- **Frontend**: Plain HTML, CSS and JavaScript, served via Nginx
- **Automated tests**: Pytest + Playwright (API and E2E, separate container, `test` profile)
- **Infra**: Docker Compose

## How to run (Docker Compose)

Prerequisite: [Docker](https://www.docker.com/) installed.

```bash
docker compose up --build
```

- Frontend: http://localhost
- Backend (API): http://localhost:3001
- Health check: http://localhost:3001/health

To run in the background:

```bash
docker compose up --build -d
```

To stop the containers:

```bash
docker compose down
```

### Environment variables

| Variable     | Description                                  | Default                |
|--------------|-----------------------------------------------|-----------------------|
| `JWT_SECRET` | Key used to sign JWT tokens                    | `dev-secret-change-me` |

To set your own value, create a `.env` file in the project root:

```
JWT_SECRET=a-very-large-secret-key
```

## How to run locally (without Docker)

### Backend

```bash
cd backend
npm install
npm run dev
```

API available at `http://localhost:3001`.

### Frontend

Serve the `frontend/` folder with any static server (e.g. VS Code's Live Server extension) or open `frontend/index.html` directly in the browser.

## Features

- User registration and login (JWT)
- Each user has their own task list
- Create, edit, complete and delete tasks
- Filters: All / Pending / Completed
- Task counter

## API

### Authentication (`/api/auth`)

| Method | Route       | Description                          |
|--------|-------------|----------------------------------------|
| POST   | `/register` | Creates a new user and returns a token |
| POST   | `/login`    | Authenticates a user and returns a token |

### Tasks (`/api/todos`)

All routes below require the `Authorization: Bearer <token>` header.

| Method | Route  | Description                  |
|--------|--------|------------------------------|
| GET    | `/`    | Lists the user's tasks       |
| POST   | `/`    | Creates a new task            |
| PUT    | `/:id` | Edits title and/or status     |
| DELETE | `/:id` | Removes a task                |

## Automated tests

API and E2E test suite in Python (Pytest + Playwright), without BDD. Runs in a separate container (`test` profile), against the already-running frontend/backend:

```bash
docker compose --profile test up tests
```

Reports are generated in `tests/playwright-report/` (HTML) and `tests/junit.xml`. Details of the testing strategy in [`tests/README.md`](tests/README.md).

## CI/CD

The suite runs on GitHub Actions ([`.github/workflows/tests.yml`](.github/workflows/tests.yml)):

| Trigger | What it runs | Why |
|---------|--------------|-----|
| **Push to `main`** | `smoke` suite | Fast feedback (~11 happy-path tests) on every change. |
| **Schedule** — daily, 06:00 UTC | Full suite (`api` + `e2e`) | Catches regressions/flakiness that only show up over time, without slowing down every push. |
| **Schedule** — Tue/Thu, 12:00 BRT | `api` suite | Recurring check on the backend layer alone. |
| **Schedule** — Wed/Fri, 12:00 BRT | `e2e` suite | Recurring check on the frontend/UI layer alone. |
| **Manual** (`workflow_dispatch`) | Choice of `all` / `api` / `e2e` / `smoke` | On-demand runs, e.g. to validate a fix or re-run only one layer. |

Each run:

1. Builds and starts `backend` and `frontend` via `docker compose` and waits
   for the backend health check.
2. Installs the Python test dependencies and Chromium (`playwright install
   --with-deps`).
3. Runs `pytest` against the running stack — already parallelized via
   `pytest-xdist` (`-n auto`, see [`tests/pytest.ini`](tests/pytest.ini)) and
   filtered by marker according to the trigger above (see
   [`tests/README.md`](tests/README.md) for what each marker covers).
4. Generates an HTML report (`pytest-html`) and a JUnit XML report.
5. Publishes a results summary as a GitHub check
   ([`dorny/test-reporter`](https://github.com/dorny/test-reporter)) and
   uploads the full HTML report and JUnit XML as workflow artifacts
   (kept for 14 days), even if the run fails.
