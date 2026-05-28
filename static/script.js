// ========== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ==========
let currentUser = null;

// Элементы
const balanceSpan = document.getElementById('balanceAmount');
const usernameSpan = document.getElementById('usernameDisplay');
const logoutBtn = document.getElementById('logoutBtn');
const toastEl = document.getElementById('toast');

// Функция показа уведомления
function showToast(message, isError = false) {
    if (!toastEl) return;
    toastEl.innerText = message;
    toastEl.className = 'toast show' + (isError ? ' error' : '');
    setTimeout(() => toastEl.classList.remove('show'), 3000);
}

// Обновление баланса с анимацией
let lastBalance = 0;
async function updateBalanceUI() {
    if (!currentUser) return;
    try {
        const res = await fetch('/api/balance');
        const data = await res.json();
        if (balanceSpan && data.balance !== undefined) {
            if (data.balance > lastBalance) {
                // Вспышка и конфетти при выигрыше
                if (data.balance - lastBalance > 500) {
                    if (window.createConfetti) window.createConfetti();
                    if (window.flashScreen) window.flashScreen('#2ecc71');
                }
                // Анимация увеличения
                balanceSpan.classList.add('pulse-gold');
                setTimeout(() => balanceSpan.classList.remove('pulse-gold'), 500);
            }
            if (window.animateNumber) {
                window.animateNumber(balanceSpan, lastBalance, data.balance, 300);
            } else {
                balanceSpan.innerText = data.balance.toFixed(0);
            }
            lastBalance = data.balance;
        }
    } catch(e) {}
}

// Авторизация
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
        document.getElementById('authPage')?.style.setProperty('display', 'none');
        document.getElementById('gameArea')?.style.setProperty('display', 'block');
        await updateBalanceUI();
        showToast(`Привет, ${currentUser.username}!`);
        loadReferralLink();
    } catch(err) {
        showToast(err.message, true);
    }
}

// Регистрация
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

// Выход
async function logout() {
    await fetch('/api/logout', { method: 'POST' });
    localStorage.removeItem('cashx_user');
    currentUser = null;
    if (usernameSpan) usernameSpan.innerText = 'Гость';
    if (logoutBtn) logoutBtn.style.display = 'none';
    document.getElementById('authPage')?.style.setProperty('display', 'block');
    document.getElementById('gameArea')?.style.setProperty('display', 'none');
    showToast('Вы вышли');
}

// Реферальная ссылка
async function loadReferralLink() {
    try {
        const res = await fetch('/api/referral/link');
        const data = await res.json();
        const refInput = document.getElementById('refLink');
        if (refInput) refInput.value = data.link;
    } catch(e) {}
}

// Инициализация обработчиков
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    if (loginForm) {
        loginForm.onsubmit = (e) => {
            e.preventDefault();
            login(
                document.getElementById('loginUsername').value,
                document.getElementById('loginPassword').value
            );
        };
    }
    if (registerForm) {
        registerForm.onsubmit = (e) => {
            e.preventDefault();
            register(
                document.getElementById('regUsername').value,
                document.getElementById('regPassword').value,
                document.getElementById('regRef').value
            );
        };
    }
    if (logoutBtn) logoutBtn.onclick = logout;
    // Восстановление сессии
    const saved = localStorage.getItem('cashx_user');
    if (saved) {
        try {
            const user = JSON.parse(saved);
            login(user.username, user.password); // упрощённо, в реальном проекте токен
        } catch(e) {}
    }
    // Периодическое обновление баланса
    if (currentUser) {
        setInterval(updateBalanceUI, 5000);
    }
});

// Чат и прочее – см. chat.js и animations.js
