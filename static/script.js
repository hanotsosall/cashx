// Глобальные переменные
let currentUser = null;

// DOM элементы
const balanceSpan = document.getElementById('balanceAmount');
const usernameSpan = document.getElementById('usernameDisplay');
const logoutBtn = document.getElementById('logoutBtn');
const toastDiv = document.getElementById('toast');

// Функция показа уведомлений
function showToast(msg, type = 'success') {
    toastDiv.innerText = msg;
    toastDiv.style.background = type === 'error' ? '#e74c3c' : '#2ecc71';
    toastDiv.classList.add('show');
    setTimeout(() => toastDiv.classList.remove('show'), 3000);
}

// Обновление баланса в UI
async function updateBalanceUI() {
    if (!currentUser) return;
    try {
        const res = await fetch('/api/balance');
        const data = await res.json();
        if (balanceSpan) balanceSpan.innerText = data.balance.toFixed(0);
    } catch(e) {}
}

// Вход
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
        // Скрыть форму авторизации, показать игры
        const authDiv = document.getElementById('authPage');
        const gameDiv = document.getElementById('gameArea');
        if (authDiv) authDiv.style.display = 'none';
        if (gameDiv) gameDiv.style.display = 'block';
        updateBalanceUI();
        showToast(`Добро пожаловать, ${currentUser.username}!`);
        // Загрузить список игр и т.д.
        loadGamesList();
    } catch (err) {
        showToast(err.message, 'error');
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
        showToast('Регистрация успешна! Выполняется вход...');
        login(username, password);
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// Выход
async function logout() {
    await fetch('/api/logout', { method: 'POST' });
    localStorage.removeItem('cashx_user');
    currentUser = null;
    if (usernameSpan) usernameSpan.innerText = 'Гость';
    if (logoutBtn) logoutBtn.style.display = 'none';
    const authDiv = document.getElementById('authPage');
    const gameDiv = document.getElementById('gameArea');
    if (authDiv) authDiv.style.display = 'block';
    if (gameDiv) gameDiv.style.display = 'none';
    showToast('Вы вышли');
}

// Проверка сохранённой сессии
function checkSession() {
    const saved = localStorage.getItem('cashx_user');
    if (saved) {
        try {
            const user = JSON.parse(saved);
            login(user.username, user.password); // пароль не храним в открытом виде, лучше использовать токен. Но для демо так.
            // В реальном проекте нужно хранить токен, а не пароль.
        } catch(e) {}
    }
}

// Загрузка списка игр (просто демо)
function loadGamesList() {
    console.log('Игры загружены');
}

// Обработчики для форм авторизации (если они есть на странице)
document.addEventListener('DOMContentLoaded', () => {
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
    checkSession();
    // Если есть чат – инициализируем
    initChat();
});

// ---------- Чат (автообновление) ----------
async function initChat() {
    const chatContainer = document.getElementById('chatMessages');
    const chatInput = document.getElementById('chatInput');
    const chatSend = document.getElementById('chatSend');
    if (!chatContainer) return;

    async function loadMessages() {
        const res = await fetch('/api/chat/messages');
        const msgs = await res.json();
        chatContainer.innerHTML = msgs.map(m => `<div><b>${escapeHtml(m.username)}</b>: ${escapeHtml(m.message)}</div>`).join('');
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    async function sendMessage() {
        const msg = chatInput.value.trim();
        if (!msg) return;
        await fetch('/api/chat/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg })
        });
        chatInput.value = '';
        loadMessages();
    }
    chatSend.onclick = sendMessage;
    chatInput.addEventListener('keypress', (e) => { if(e.key === 'Enter') sendMessage(); });
    setInterval(loadMessages, 3000);
    loadMessages();
}

function escapeHtml(str) {
    return str.replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}
