// ========== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ==========
let currentUser = null;

// DOM элементы
const balanceSpan = document.getElementById('balanceAmount');
const usernameSpan = document.getElementById('usernameDisplay');
const logoutBtn = document.getElementById('logoutBtn');
const loginNavBtn = document.getElementById('loginNavBtn');
const toastEl = document.getElementById('toast');

// ========== УВЕДОМЛЕНИЯ ==========
function showToast(msg, isError = false) {
    if (!toastEl) return;
    toastEl.innerText = msg;
    toastEl.className = 'toast show' + (isError ? ' error' : '');
    setTimeout(() => toastEl.classList.remove('show'), 3000);
}

// ========== ОБНОВЛЕНИЕ БАЛАНСА В UI ==========
async function updateBalanceUI() {
    if (!currentUser) return;
    try {
        const res = await fetch('/api/balance');
        if (res.status === 401) {
            showAuthState(false);
            return;
        }
        const data = await res.json();
        if (balanceSpan) {
            const oldVal = parseInt(balanceSpan.innerText) || 0;
            const newVal = data.balance;
            balanceSpan.innerText = newVal.toFixed(0);
            if (newVal > oldVal) {
                balanceSpan.classList.add('pulse-gold');
                setTimeout(() => balanceSpan.classList.remove('pulse-gold'), 500);
                if (newVal - oldVal > 500 && window.createConfetti) window.createConfetti();
            }
        }
    } catch(e) { console.error(e); }
}

// ========== УПРАВЛЕНИЕ СОСТОЯНИЕМ АВТОРИЗАЦИИ ==========
function showAuthState(isLoggedIn) {
    if (isLoggedIn && currentUser) {
        if (loginNavBtn) loginNavBtn.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'inline-block';
        if (usernameSpan) usernameSpan.innerText = currentUser.username;
        // Показать контент, скрыть страницу логина (если она видна)
        const loginPage = document.getElementById('loginPageContainer');
        if (loginPage) loginPage.style.display = 'none';
        const mainContent = document.getElementById('mainContent');
        if (mainContent) mainContent.style.display = 'block';
    } else {
        if (loginNavBtn) loginNavBtn.style.display = 'inline-block';
        if (logoutBtn) logoutBtn.style.display = 'none';
        if (usernameSpan) usernameSpan.innerText = 'Гость';
        currentUser = null;
        localStorage.removeItem('cashx_user');
        // Показать страницу логина, скрыть контент
        const loginPage = document.getElementById('loginPageContainer');
        if (loginPage) loginPage.style.display = 'flex';
        const mainContent = document.getElementById('mainContent');
        if (mainContent) mainContent.style.display = 'none';
    }
}

// ========== API ВЗАИМОДЕЙСТВИЯ ==========
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
        // Если есть реферальная ссылка на странице профиля – обновим
        if (document.getElementById('refLink')) loadReferralLink();
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
            if (document.getElementById('refLink')) loadReferralLink();
        } else {
            showAuthState(false);
        }
    } catch(e) {
        showAuthState(false);
    }
}

// ========== РЕФЕРАЛЬНАЯ ССЫЛКА ==========
async function loadReferralLink() {
    if (!currentUser) return;
    try {
        const res = await fetch('/api/referral/link');
        const data = await res.json();
        const refInput = document.getElementById('refLink');
        if (refInput) refInput.value = data.link;
    } catch(e) {}
}

// ========== ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ ==========
document.addEventListener('DOMContentLoaded', () => {
    // Кнопки входа/выхода
    if (loginNavBtn) {
        loginNavBtn.onclick = () => window.location.href = '/login';
    }
    if (logoutBtn) logoutBtn.onclick = logout;

    // Формы на странице /login (если они есть)
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

    // Проверка авторизации
    checkAuth();

    // Периодическое обновление баланса
    setInterval(() => {
        if (currentUser) updateBalanceUI();
    }, 5000);

    // Эффект для онлайн-счётчика
    const onlineSpan = document.getElementById('onlineCount');
    if (onlineSpan) {
        let online = 1234;
        setInterval(() => {
            const delta = Math.floor(Math.random() * 11) - 5;
            online += delta;
            if (online < 800) online = 1200;
            onlineSpan.innerText = online.toLocaleString();
        }, 8000);
    }

    // Подсветка активного пункта меню
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.style.color = '#f5b042';
            link.style.borderLeftColor = '#f5b042';
        }
    });
});

// ========== ДОПОЛНИТЕЛЬНЫЕ ЭФФЕКТЫ (конфетти, вспышка) ==========
function createConfetti() {
    const colors = ['#f5b042', '#ffd966', '#ff8800', '#ffffff', '#2ecc71'];
    for (let i = 0; i < 100; i++) {
        const conf = document.createElement('div');
        conf.style.position = 'fixed';
        conf.style.width = Math.random() * 10 + 4 + 'px';
        conf.style.height = Math.random() * 6 + 4 + 'px';
        conf.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        conf.style.left = Math.random() * window.innerWidth + 'px';
        conf.style.top = '-20px';
        conf.style.zIndex = '10000';
        conf.style.pointerEvents = 'none';
        conf.style.borderRadius = Math.random() > 0.5 ? '50%' : '0';
        conf.style.animation = `fall ${Math.random() * 2 + 1.5}s linear forwards`;
        document.body.appendChild(conf);
        setTimeout(() => conf.remove(), 3000);
    }
}

function flashScreen(color = '#f5b042') {
    const flash = document.createElement('div');
    flash.style.position = 'fixed';
    flash.style.top = 0;
    flash.style.left = 0;
    flash.style.width = '100%';
    flash.style.height = '100%';
    flash.style.backgroundColor = color;
    flash.style.zIndex = '9999';
    flash.style.pointerEvents = 'none';
    flash.style.opacity = '0.6';
    flash.style.transition = 'opacity 0.3s ease';
    document.body.appendChild(flash);
    setTimeout(() => {
        flash.style.opacity = '0';
        setTimeout(() => flash.remove(), 300);
    }, 100);
}

window.createConfetti = createConfetti;
window.flashScreen = flashScreen;

// Добавляем ключевые кадры для анимации конфетти
const style = document.createElement('style');
style.textContent = `
    @keyframes fall {
        0% { transform: translateY(0) rotate(0deg); opacity: 1; }
        100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
    }
    @keyframes pulse-gold {
        0% { text-shadow: 0 0 0 gold; transform: scale(1); }
        50% { text-shadow: 0 0 20px gold; transform: scale(1.1); }
        100% { text-shadow: 0 0 0 gold; transform: scale(1); }
    }
    .pulse-gold { animation: pulse-gold 0.5s ease-out; }
`;
document.head.appendChild(style);
