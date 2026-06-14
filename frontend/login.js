const API = `${window.location.protocol}//${window.location.hostname}/api/auth`;

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PASSWORD_REGEX = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z0-9]{6,}$/;

const usernameInput = document.getElementById("username-input");
const passwordInput = document.getElementById("password-input");
const usernameError = document.getElementById("username-error");
const passwordError = document.getElementById("password-error");
const errorMsg      = document.getElementById("error-msg");
const successMsg    = document.getElementById("success-msg");
const loginBtn      = document.getElementById("login-btn");

// If there is already an active session, go straight to the task list
if (getToken()) {
  window.location.href = "index.html";
}

// Success message after registration
if (new URLSearchParams(window.location.search).get("registered") === "1") {
  successMsg.textContent = "Registration successful! Please log in to continue.";
}

loginBtn.addEventListener("click", login);
passwordInput.addEventListener("keydown", e => { if (e.key === "Enter") login(); });

setupPasswordToggle("toggle-password", "password-input");

// ── Real-time validation (enables/disables the button) ──
function isValid() {
  const email = usernameInput.value.trim();
  const password = passwordInput.value;

  return EMAIL_REGEX.test(email) && PASSWORD_REGEX.test(password);
}

function updateButtonState() {
  loginBtn.disabled = !isValid();
}

usernameInput.addEventListener("input", updateButtonState);
passwordInput.addEventListener("input", updateButtonState);
updateButtonState();

function showFieldErrors() {
  const email = usernameInput.value.trim();
  const password = passwordInput.value;

  if (!EMAIL_REGEX.test(email)) {
    usernameError.textContent = "Please enter a valid email.";
  }

  if (!PASSWORD_REGEX.test(password)) {
    passwordError.textContent = "Password must be at least 6 characters, with letters and numbers.";
  }
}

async function login() {
  errorMsg.textContent = "";
  usernameError.textContent = "";
  passwordError.textContent = "";

  if (!isValid()) {
    showFieldErrors();
    return;
  }

  const email = usernameInput.value.trim();
  const password = passwordInput.value;

  const res = await fetch(`${API}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: email, password }),
  });

  const data = await res.json();

  if (!res.ok) {
    errorMsg.textContent = data.error;
    return;
  }

  setSession(data.token, data.username);
  window.location.href = "index.html";
}
