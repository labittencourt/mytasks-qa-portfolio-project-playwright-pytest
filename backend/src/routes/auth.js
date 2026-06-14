const express = require("express");
const router = express.Router();
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const db = require("../database");
const { JWT_SECRET } = require("../middleware/auth");

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PASSWORD_REGEX = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z0-9]{6,}$/;

// POST /api/auth/register — create new user
router.post("/register", (req, res) => {
  const { username, password } = req.body;

  if (!username || !username.trim() || !password) {
    return res.status(400).json({ error: "Email and password are required" });
  }

  const trimmedUsername = username.trim();

  if (!EMAIL_REGEX.test(trimmedUsername)) {
    return res.status(400).json({ error: "Please enter a valid email" });
  }

  if (!PASSWORD_REGEX.test(password)) {
    return res.status(400).json({ error: "Password must be at least 6 characters, containing letters and numbers" });
  }

  const existing = db.prepare("SELECT id FROM users WHERE username = ?").get(trimmedUsername);
  if (existing) {
    return res.status(409).json({ error: "User already exists" });
  }

  const passwordHash = bcrypt.hashSync(password, 10);
  const result = db
    .prepare("INSERT INTO users (username, password_hash) VALUES (?, ?)")
    .run(trimmedUsername, passwordHash);

  const token = jwt.sign({ userId: result.lastInsertRowid }, JWT_SECRET, { expiresIn: "7d" });
  res.status(201).json({ token, username: trimmedUsername });
});

// POST /api/auth/login — authenticate existing user
router.post("/login", (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: "Email and password are required" });
  }

  const trimmedUsername = username.trim();

  if (!EMAIL_REGEX.test(trimmedUsername)) {
    return res.status(400).json({ error: "Please enter a valid email" });
  }

  const user = db.prepare("SELECT * FROM users WHERE username = ?").get(trimmedUsername);
  if (!user || !bcrypt.compareSync(password, user.password_hash)) {
    return res.status(401).json({ error: "Invalid username or password" });
  }

  const token = jwt.sign({ userId: user.id }, JWT_SECRET, { expiresIn: "7d" });
  res.json({ token, username: user.username });
});

module.exports = router;
