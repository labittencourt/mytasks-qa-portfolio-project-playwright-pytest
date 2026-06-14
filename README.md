# QA Portfolio — Todo List

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
