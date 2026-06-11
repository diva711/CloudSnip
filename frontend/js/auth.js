const API = 'http://3.111.214.60:5000';

function getToken() {
  return localStorage.getItem('token');
}

function saveToken(token) {
  localStorage.setItem('token', token);
}

function clearToken() {
  localStorage.removeItem('token');
}

function redirectIfLoggedIn() {
  if (getToken()) {
    window.location.href = 'index.html';
  }
}

function redirectIfNotLoggedIn() {
  if (!getToken()) {
    window.location.href = 'login.html';
  }
}

function logout() {
  clearToken();
  window.location.href = 'login.html';
}

function showTab(tab) {
  document.getElementById('loginForm').style.display = tab === 'login' ? 'block' : 'none';
  document.getElementById('registerForm').style.display = tab === 'register' ? 'block' : 'none';
  document.querySelectorAll('.tab').forEach((t, i) => {
    t.classList.toggle('active',
      (tab === 'login' && i === 0) || (tab === 'register' && i === 1)
    );
  });
}

async function login() {
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;
  const msg = document.getElementById('loginMessage');

  try {
    const res = await fetch(`${API}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();

    if (data.token) {
      saveToken(data.token);
      window.location.href = 'index.html';
    } else {
      msg.className = 'message error';
      msg.textContent = data.error || 'Login failed';
    }
  } catch {
    msg.className = 'message error';
    msg.textContent = 'Could not connect to server';
  }
}

async function register() {
  const email = document.getElementById('registerEmail').value;
  const password = document.getElementById('registerPassword').value;
  const msg = document.getElementById('registerMessage');

  try {
    const res = await fetch(`${API}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();

    if (res.status === 201) {
      msg.className = 'message success';
      msg.textContent = 'Account created! Please login.';
      setTimeout(() => showTab('login'), 1500);
    } else {
      msg.className = 'message error';
      msg.textContent = data.error || 'Registration failed';
    }
  } catch {
    msg.className = 'message error';
    msg.textContent = 'Could not connect to server';
  }
}