const API = `${window.location.protocol}//${window.location.hostname}/api/auth`;

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PASSWORD_REGEX = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z0-9]{6,}$/;

const usernameInput        = document.getElementById("username-input");
const passwordInput        = document.getElementById("password-input");
const confirmPasswordInput = document.getElementById("confirm-password-input");
const usernameError        = document.getElementById("username-error");
const passwordError        = document.getElementById("password-error");
const confirmPasswordError = document.getElementById("confirm-password-error");
const errorMsg             = document.getElementById("error-msg");
const registerBtn          = document.getElementById("register-btn");

// If there is already an active session, go straight to the task list
if (getToken()) {
  window.location.href = "index.html";
}

registerBtn.addEventListener("click", register);
confirmPasswordInput.addEventListener("keydown", e => { if (e.key === "Enter") register(); });

setupPasswordToggle("toggle-password", "password-input");
setupPasswordToggle("toggle-confirm-password", "confirm-password-input");

// ── Real-time validation (enables/disables the button) ──
function isValid() {
  const email = usernameInput.value.trim();
  const password = passwordInput.value;
  const confirmPassword = confirmPasswordInput.value;

  return EMAIL_REGEX.test(email) && PASSWORD_REGEX.test(password) && password === confirmPassword;
}

function updateButtonState() {
  registerBtn.disabled = !isValid();
}

usernameInput.addEventListener("input", updateButtonState);
passwordInput.addEventListener("input", updateButtonState);
confirmPasswordInput.addEventListener("input", updateButtonState);
updateButtonState();

function showFieldErrors() {
  const email = usernameInput.value.trim();
  const password = passwordInput.value;
  const confirmPassword = confirmPasswordInput.value;

  if (!EMAIL_REGEX.test(email)) {
    usernameError.textContent = "Please enter a valid email.";
  }

  if (!PASSWORD_REGEX.test(password)) {
    passwordError.textContent = "Password must be at least 6 characters, with letters and numbers.";
  }

  if (password !== confirmPassword) {
    confirmPasswordError.textContent = "Passwords do not match.";
  }
}

async function register() {
  errorMsg.textContent = "";
  usernameError.textContent = "";
  passwordError.textContent = "";
  confirmPasswordError.textContent = "";

  if (!isValid()) {
    showFieldErrors();
    return;
  }

  const email = usernameInput.value.trim();
  const password = passwordInput.value;

  const res = await fetch(`${API}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: email, password }),
  });

  const data = await res.json();

  if (!res.ok) {
    errorMsg.textContent = data.error;
    return;
  }

  window.location.href = "login.html?registered=1";
}
