let chatInterval = null;

async function loadChatMessages() {
    try {
        const res = await fetch('/api/chat/messages');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const msgs = await res.json();
        const container = document.getElementById('chatMessages');
        if (!container) return;
        container.innerHTML = msgs.map(m => `
            <div class="chat-message">
                <strong>${escapeHtml(m.username)}</strong>:
                <span>${escapeHtml(m.message)}</span>
                <small>${new Date(m.time).toLocaleTimeString()}</small>
            </div>
        `).join('');
        container.scrollTop = container.scrollHeight;
    } catch(e) {
        console.error('loadChatMessages error:', e);
    }
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const msg = input.value.trim();
    if (!msg) return;
    try {
        const res = await fetch('/api/chat/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg })
        });
        if (res.status === 401) {
            showToast('❌ Вы не авторизованы. Войдите, чтобы писать в чат.', true);
            return;
        }
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (data.ok) {
            input.value = '';
            loadChatMessages();
        } else {
            showToast(data.error || 'Ошибка отправки', true);
        }
    } catch(e) {
        console.error('sendChatMessage error:', e);
        showToast('Ошибка отправки сообщения', true);
    }
}

function escapeHtml(str) {
    return str.replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

function initChat() {
    const sendBtn = document.getElementById('chatSendBtn');
    const chatInput = document.getElementById('chatInput');
    if (sendBtn && chatInput) {
        sendBtn.onclick = sendChatMessage;
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendChatMessage();
        });
        loadChatMessages();
        if (chatInterval) clearInterval(chatInterval);
        chatInterval = setInterval(loadChatMessages, 3000);
    } else {
        setTimeout(initChat, 500);
    }
}

document.addEventListener('DOMContentLoaded', initChat);
