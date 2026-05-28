async function loadChat() {
    const res = await fetch('/api/chat/messages');
    const msgs = await res.json();
    const container = document.getElementById('chatMessages');
    if(container) container.innerHTML = msgs.map(m => `<div><b>${escapeHtml(m.username)}</b>: ${escapeHtml(m.message)}</div>`).join('');
}
async function sendChat() {
    const input = document.getElementById('chatInput');
    const msg = input.value.trim();
    if(!msg) return;
    await fetch('/api/chat/send', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
    input.value = '';
    loadChat();
}
function escapeHtml(s) { return s.replace(/[&<>]/g, function(m){ if(m==='&') return '&amp;'; if(m==='<') return '&lt;'; if(m==='>') return '&gt;'; return m;}); }
if(document.getElementById('chatSend')) document.getElementById('chatSend').onclick = sendChat;
if(document.getElementById('chatInput')) setInterval(loadChat, 3000);
