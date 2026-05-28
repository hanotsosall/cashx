let currentUser = null;
async function updateBalanceUI() {
    if(!currentUser) return;
    const res = await fetch('/api/user');
    const data = await res.json();
    document.getElementById('mainBalance').innerText = data.balance;
    document.getElementById('bonusBalance').innerText = data.bonus_balance;
}
async function login(username, password) {
    const res = await fetch('/api/login', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username,password})});
    const data = await res.json();
    if(data.error) return alert(data.error);
    currentUser = data.user;
    localStorage.setItem('user', JSON.stringify(currentUser));
    document.getElementById('usernameDisplay').innerText = currentUser.username;
    document.getElementById('logoutBtn').style.display = 'inline-block';
    document.getElementById('authPage').style.display = 'none';
    document.getElementById('gameArea').style.display = 'block';
    updateBalanceUI();
}
async function register(username, password, ref) {
    const res = await fetch('/api/register', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username,password,ref_code:ref})});
    const data = await res.json();
    if(data.error) return alert(data.error);
    login(username, password);
}
document.getElementById('doLogin')?.addEventListener('click',()=>login(document.getElementById('loginUser').value, document.getElementById('loginPass').value));
document.getElementById('doReg')?.addEventListener('click',()=>register(document.getElementById('regUser').value, document.getElementById('regPass').value, document.getElementById('regRef').value));
document.getElementById('logoutBtn')?.addEventListener('click', async ()=>{ await fetch('/api/logout',{method:'POST'}); localStorage.clear(); location.reload(); });
// Восстановление сессии
const saved = localStorage.getItem('user');
if(saved) { currentUser = JSON.parse(saved); document.getElementById('usernameDisplay').innerText = currentUser.username; document.getElementById('logoutBtn').style.display = 'inline-block'; document.getElementById('authPage').style.display = 'none'; document.getElementById('gameArea').style.display = 'block'; updateBalanceUI(); }
// Мобильное меню
document.getElementById('mobileMenuToggle')?.addEventListener('click',()=>document.getElementById('sidebar').classList.toggle('open'));
setInterval(()=>{ if(currentUser) updateBalanceUI(); }, 5000);
