let currentUser = null;

const balanceSpan = document.getElementById('balanceAmount');
const usernameSpan = document.getElementById('usernameDisplay');
const logoutBtn = document.getElementById('logoutBtn');
const loginNavBtn = document.getElementById('loginNavBtn');
const toastEl = document.getElementById('toast');

function showToast(msg, isError = false) {
    if (!toastEl) return;
    toastEl.innerText = msg;
    toastEl.className = 'toast show' + (isError ? ' error' : '');
    setTimeout(() => toastEl.classList.remove('show'), 3000);
}

async function updateBalanceUI() {
    if (!currentUser) return;
    try {
        const res = await fetch('/api/balance');
        if (res.status === 401) {
            showAuthState(false);
            return;
        }
        const data = await res.json();
        if (balanceSpan) balanceSpan.innerText = data.balance.toFixed(0);
    } catch(e) {}
}

function showAuthState(isLoggedIn) {
    if (isLoggedIn) {
        if (loginNavBtn) loginNavBtn.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'inline-block';
        if (usernameSpan && currentUser) usernameSpan.innerText = currentUser.username;
    } else {
        if (loginNavBtn) loginNavBtn.style.display = 'inline-block';
        if (logoutBtn) logoutBtn.style.display = 'none';
        if (usernameSpan) usernameSpan.innerText = 'Гость';
        currentUser = null;
        localStorage.removeItem('cashx_user');
    }
}

async function login(username, password) {
    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        currentUser = data.user;
        localStorage.setItem('cashx_user', JSON.stringify(currentUser));
        showAuthState(true);
        await updateBalanceUI();
        showToast(`Добро пожаловать, ${currentUser.username}!`);
    } catch(err) {
        showToast(err.message, true);
    }
}

async function register(username, password, refCode) {
    try {
        const res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, ref_code: refCode })
        });
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        showToast('Регистрация успешна! Вход...');
        login(username, password);
    } catch(err) {
        showToast(err.message, true);
    }
}

async function logout() {
    await fetch('/api/logout', { method: 'POST' });
    showAuthState(false);
    showToast('Вы вышли');
}

async function checkAuth() {
    try {
        const res = await fetch('/api/user');
        if (res.status === 200) {
            const data = await res.json();
            currentUser = data;
            localStorage.setItem('cashx_user', JSON.stringify(currentUser));
            showAuthState(true);
            updateBalanceUI();
        } else {
            showAuthState(false);
        }
    } catch(e) {
        showAuthState(false);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Кнопка входа в шапке
    if (loginNavBtn) {
        loginNavBtn.onclick = () => window.location.href = '/login';
    }
    if (logoutBtn) logoutBtn.onclick = logout;

    // Авторизация через отдельную страницу (формы на /login)
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    if (loginForm) {
        loginForm.onsubmit = (e) => {
            e.preventDefault();
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            login(username, password);
        };
    }
    if (registerForm) {
        registerForm.onsubmit = (e) => {
            e.preventDefault();
            const username = document.getElementById('regUsername').value;
            const password = document.getElementById('regPassword').value;
            const ref = document.getElementById('regRef').value;
            register(username, password, ref);
        };
    }

    checkAuth();
    setInterval(() => { if (currentUser) updateBalanceUI(); }, 5000);
});
