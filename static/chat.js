// Автономный чат-виджет (можно вставить в layout.html)
let chatInterval = null;

async function loadChatMessages() {
    try {
        const res = await fetch('/api/chat/messages');
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
    } catch(e) {}
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const msg = input.value.trim();
    if (!msg) return;
    try {
        await fetch('/api/chat/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg })
        });
        input.value = '';
        loadChatMessages();
    } catch(e) {}
}

function escapeHtml(str) {
    return str.replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const sendBtn = document.getElementById('chatSend');
    const chatInput = document.getElementById('chatInput');
    if (sendBtn) {
        sendBtn.onclick = sendChatMessage;
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendChatMessage();
            });
        }
        loadChatMessages();
        if (chatInterval) clearInterval(chatInterval);
        chatInterval = setInterval(loadChatMessages, 3000);
    }
});
