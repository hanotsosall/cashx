let currentUser = null;

const balanceSpan = document.getElementById('balanceAmount');
const usernameSpan = document.getElementById('usernameDisplay');
const logoutBtn = document.getElementById('logoutBtn');
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
            // Сессия истекла – показываем вход
            showAuthPage();
            return;
        }
        const data = await res.json();
        if (balanceSpan) balanceSpan.innerText = data.balance.toFixed(0);
    } catch(e) {}
}

function showAuthPage() {
    document.getElementById('authPage')?.style.setProperty('display', 'flex');
    document.getElementById('gameArea')?.style.setProperty('display', 'none');
    if (logoutBtn) logoutBtn.style.display = 'none';
    if (usernameSpan) usernameSpan.innerText = 'Гость';
    currentUser = null;
    localStorage.removeItem('cashx_user');
}

function showGameArea() {
    document.getElementById('authPage')?.style.setProperty('display', 'none');
    document.getElementById('gameArea')?.style.setProperty('display', 'block');
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
        if (usernameSpan) usernameSpan.innerText = currentUser.username;
        if (logoutBtn) logoutBtn.style.display = 'inline-block';
        showGameArea();
        await updateBalanceUI();
        showToast(`Добро пожаловать, ${currentUser.username}!`);
        loadReferralLink();
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
        showToast('Регистрация успешна! Выполняется вход...');
        login(username, password);
    } catch(err) {
        showToast(err.message, true);
    }
}

async function logout() {
    await fetch('/api/logout', { method: 'POST' });
    localStorage.removeItem('cashx_user');
    showAuthPage();
    showToast('Вы вышли');
}

async function checkAuth() {
    try {
        const res = await fetch('/api/user');
        if (res.status === 200) {
            const data = await res.json();
            currentUser = data;
            localStorage.setItem('cashx_user', JSON.stringify(currentUser));
            if (usernameSpan) usernameSpan.innerText = currentUser.username;
            if (logoutBtn) logoutBtn.style.display = 'inline-block';
            showGameArea();
            updateBalanceUI();
            loadReferralLink();
        } else {
            showAuthPage();
        }
    } catch(e) {
        showAuthPage();
    }
}

async function loadReferralLink() {
    if (!currentUser) return;
    try {
        const res = await fetch('/api/referral/link');
        const data = await res.json();
        const refInput = document.getElementById('refLink');
        if (refInput) refInput.value = data.link;
    } catch(e) {}
}

// ---------- Обработчики при загрузке страницы ----------
document.addEventListener('DOMContentLoaded', () => {
    // Формы авторизации
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
    if (logoutBtn) logoutBtn.onclick = logout;
    // Проверка существующей сессии
    checkAuth();

    // Мобильное меню
    const menuToggle = document.getElementById('mobileMenuToggle');
    const sidebar = document.getElementById('sidebar');
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            menuToggle.innerHTML = sidebar.classList.contains('open') ? '✕' : '☰';
        });
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    sidebar.classList.remove('open');
                    menuToggle.innerHTML = '☰';
                }
            });
        });
    }

    // Обновление баланса каждые 5 секунд
    setInterval(() => {
        if (currentUser) updateBalanceUI();
    }, 5000);
});
