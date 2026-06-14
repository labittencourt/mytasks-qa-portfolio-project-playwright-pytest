const express = require("express");
const router = express.Router();
const db = require("../database");
const { authMiddleware } = require("../middleware/auth");

// All task routes require authentication
router.use(authMiddleware);

// GET /api/todos — list the authenticated user's tasks
router.get("/", (req, res) => {
  const todos = db
    .prepare("SELECT * FROM todos WHERE user_id = ? ORDER BY created_at DESC")
    .all(req.userId);
  res.json(todos);
});

// POST /api/todos — create new task
router.post("/", (req, res) => {
  const { title } = req.body;

  if (!title || title.trim() === "") {
    return res.status(400).json({ error: "Title is required" });
  }

  const result = db
    .prepare("INSERT INTO todos (title, user_id) VALUES (?, ?)")
    .run(title.trim(), req.userId);

  const todo = db
    .prepare("SELECT * FROM todos WHERE id = ?")
    .get(result.lastInsertRowid);

  res.status(201).json(todo);
});

// PUT /api/todos/:id — edit task
router.put("/:id", (req, res) => {
  const { id } = req.params;
  const { title, completed } = req.body;

  const todo = db.prepare("SELECT * FROM todos WHERE id = ? AND user_id = ?").get(id, req.userId);
  if (!todo) return res.status(404).json({ error: "Task not found" });

  const newTitle = title !== undefined ? title.trim() : todo.title;
  const newCompleted = completed !== undefined ? (completed ? 1 : 0) : todo.completed;

  if (newTitle === "") {
    return res.status(400).json({ error: "Title is required" });
  }

  db.prepare("UPDATE todos SET title = ?, completed = ? WHERE id = ?")
    .run(newTitle, newCompleted, id);

  const updated = db.prepare("SELECT * FROM todos WHERE id = ?").get(id);
  res.json(updated);
});

// DELETE /api/todos/:id — delete task
router.delete("/:id", (req, res) => {
  const { id } = req.params;

  const todo = db.prepare("SELECT * FROM todos WHERE id = ? AND user_id = ?").get(id, req.userId);
  if (!todo) return res.status(404).json({ error: "Task not found" });

  db.prepare("DELETE FROM todos WHERE id = ?").run(id);
  res.status(204).send();
});

module.exports = router;
