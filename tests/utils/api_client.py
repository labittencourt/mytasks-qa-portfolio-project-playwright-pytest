import requests


class ApiClient:
    """Thin wrapper over requests for the backend API endpoints."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    @staticmethod
    def _headers(token=None):
        return {"Authorization": f"Bearer {token}"} if token else {}

    def get(self, path, token=None):
        return requests.get(f"{self.base_url}{path}", headers=self._headers(token), timeout=10)

    def post(self, path, json=None, token=None):
        return requests.post(f"{self.base_url}{path}", json=json, headers=self._headers(token), timeout=10)

    def put(self, path, json=None, token=None):
        return requests.put(f"{self.base_url}{path}", json=json, headers=self._headers(token), timeout=10)

    def delete(self, path, token=None):
        return requests.delete(f"{self.base_url}{path}", headers=self._headers(token), timeout=10)

    # Domain-specific shortcuts
    def register(self, email, password):
        return self.post("/api/auth/register", json={"username": email, "password": password})

    def login(self, email, password):
        return self.post("/api/auth/login", json={"username": email, "password": password})

    def health(self):
        return self.get("/health")

    def list_todos(self, token):
        return self.get("/api/todos", token=token)

    def create_todo(self, token, title):
        return self.post("/api/todos", json={"title": title}, token=token)

    def update_todo(self, token, todo_id, **fields):
        return self.put(f"/api/todos/{todo_id}", json=fields, token=token)

    def delete_todo(self, token, todo_id):
        return self.delete(f"/api/todos/{todo_id}", token=token)
