const TOKEN_KEY = "todo_token";
const USERNAME_KEY = "todo_username";

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function getUsername() {
  return localStorage.getItem(USERNAME_KEY);
}

function setSession(token, username) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USERNAME_KEY, username);
}

function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USERNAME_KEY);
}

// Redirects to login if there is no active session
function requireAuth() {
  if (!getToken()) {
    window.location.href = "login.html";
  }
}

function logout() {
  clearSession();
  window.location.href = "login.html";
}

// Wires up the "eye" button that toggles password visibility
function setupPasswordToggle(toggleId, inputId) {
  const toggle = document.getElementById(toggleId);
  const input = document.getElementById(inputId);

  toggle.addEventListener("click", () => {
    const showing = input.type === "text";
    input.type = showing ? "password" : "text";
    toggle.textContent = showing ? "👁" : "🙈";
    toggle.setAttribute("aria-label", showing ? "Show password" : "Hide password");
  });
}
