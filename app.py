import os
import bcrypt
import secrets
import json
import random
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from config import Config
from models import db, User, Transaction, WithdrawRequest, GameSession, ChatMessage

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        hashed = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
        admin = User(username='admin', password=hashed, is_admin=True, balance=1000000)
        db.session.add(admin)
        db.session.commit()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            return jsonify({'error': 'Forbidden'}), 403
        return f(*args, **kwargs)
    return decorated

# ---------- Страницы ----------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/games')
def games():
    return render_template('games.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/game/slots')
def game_slots():
    return render_template('game_slots.html')

@app.route('/game/mines')
def game_mines():
    return render_template('game_mines.html')

@app.route('/game/crash')
def game_crash():
    return render_template('game_crash.html')

@app.route('/game/dice')
def game_dice():
    return render_template('game_dice.html')

@app.route('/game/coinflip')
def game_coinflip():
    return render_template('game_coinflip.html')

@app.route('/game/keno')
def game_keno():
    return render_template('game_keno.html')

@app.route('/game/boomcity')
def game_boomcity():
    return render_template('game_boomcity.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

# ---------- API ----------
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    ref = data.get('ref_code', '')
    if not username or not password:
        return jsonify({'error': 'Заполните поля'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Имя занято'}), 400
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User(username=username, password=hashed)
    if ref:
        referrer = User.query.filter_by(username=ref).first()
        if referrer:
            user.referrer_id = referrer.id
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.id
    session['username'] = user.username
    return jsonify({'ok': True, 'user': {'id': user.id, 'username': user.username, 'balance': user.balance, 'is_admin': user.is_admin}})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.checkpw(password.encode(), user.password.encode()):
        return jsonify({'error': 'Неверные данные'}), 401
    session['user_id'] = user.id
    session['username'] = user.username
    return jsonify({'ok': True, 'user': {'id': user.id, 'username': user.username, 'balance': user.balance, 'is_admin': user.is_admin}})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'ok': True})

@app.route('/api/user')
def get_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = User.query.get(session['user_id'])
    return jsonify({'id': user.id, 'username': user.username, 'balance': user.balance, 'is_admin': user.is_admin})

@app.route('/api/balance')
@login_required
def get_balance():
    user = User.query.get(session['user_id'])
    return jsonify({'balance': user.balance})

# ---------- Игровые API (реалистичные заглушки, можно доработать) ----------
@app.route('/api/slots/spin', methods=['POST'])
@login_required
def slots_spin():
    bet = request.json.get('bet', 10)
    symbols = ['🍒','🍋','🍊','🍉','💎','7️⃣','🐉']
    reels = [[random.choice(symbols) for _ in range(3)] for _ in range(5)]
    win = 0
    for row in range(3):
        if reels[0][row] == reels[1][row] == reels[2][row] == reels[3][row] == reels[4][row]:
            mult = {'🍒':2, '🍋':3, '🍊':4, '🍉':5, '💎':10, '7️⃣':20, '🐉':50}.get(reels[0][row], 1)
            win += bet * mult
    if all(reels[i][1] == '🐉' for i in range(5)):
        win += 5000
    return jsonify({'reels': reels, 'win': win})

@app.route('/api/mines/generate', methods=['POST'])
@login_required
def mines_generate():
    mines = request.json.get('mines', 3)
    bet = request.json.get('bet', 10)
    grid = [[0]*5 for _ in range(5)]
    positions = [(i,j) for i in range(5) for j in range(5)]
    for _ in range(mines):
        r,c = random.choice(positions)
        grid[r][c] = 1
        positions.remove((r,c))
    return jsonify({'grid': grid, 'bet': bet})

@app.route('/api/mines/reveal', methods=['POST'])
@login_required
def mines_reveal():
    row = request.json.get('row')
    col = request.json.get('col')
    # Для демо всегда безопасно
    return jsonify({'boom': False, 'multiplier': 1.5})

@app.route('/api/crash/start', methods=['POST'])
@login_required
def crash_start():
    bet = request.json.get('bet', 10)
    session_id = secrets.token_urlsafe(16)
    return jsonify({'session_id': session_id, 'balance': 1000})

@app.route('/api/crash/cashout', methods=['POST'])
@login_required
def crash_cashout():
    return jsonify({'win': 200, 'multiplier': 2.0, 'balance': 1200})

@app.route('/api/crash/status', methods=['GET'])
def crash_status():
    return jsonify({'running': True, 'multiplier': round(random.uniform(1.0, 5.0), 2)})

@app.route('/api/dice/roll', methods=['POST'])
@login_required
def dice_roll():
    bet = request.json.get('bet', 10)
    pred = request.json.get('prediction')
    target = request.json.get('target', 50)
    roll = random.randint(1,100)
    win = 0
    if pred == 'under' and roll < target:
        win = int(bet * 1.98)
    elif pred == 'over' and roll > target:
        win = int(bet * 1.98)
    elif pred == 'number' and roll == target:
        win = bet * 50
    return jsonify({'roll': roll, 'win': win})

@app.route('/api/coinflip/flip', methods=['POST'])
@login_required
def coinflip_flip():
    bet = request.json.get('bet', 10)
    choice = request.json.get('choice')
    result = random.choice(['heads', 'tails'])
    win = bet * 2 if choice == result else 0
    return jsonify({'result': result, 'win': win})

@app.route('/api/keno/draw', methods=['POST'])
@login_required
def keno_draw():
    bet = request.json.get('bet', 10)
    picks = request.json.get('picks', [])
    drawn = random.sample(range(1,81), 20)
    matches = len(set(picks) & set(drawn))
    win = matches * (bet // 10) * 2
    return jsonify({'drawn': drawn, 'matches': matches, 'win': win})

@app.route('/api/boomcity/spin', methods=['POST'])
@login_required
def boomcity_spin():
    bet = request.json.get('bet', 10)
    win = random.choice([0, bet, bet*2, bet*5])
    return jsonify({'win': win})

@app.route('/api/place_bet', methods=['POST'])
@login_required
def place_bet():
    data = request.json
    bet = data.get('bet', 0)
    win = data.get('win', 0)
    user = User.query.get(session['user_id'])
    if bet > 0 and user.balance < bet:
        return jsonify({'error': 'Недостаточно средств'}), 400
    user.balance = user.balance - bet + win
    db.session.commit()
    return jsonify({'balance': user.balance})

# ---------- Бонусы, рефералы, чат, админка ----------
@app.route('/api/bonus/apply', methods=['POST'])
@login_required
def apply_bonus():
    return jsonify({'error': 'Код не найден'}), 400

@app.route('/api/referral/link')
@login_required
def referral_link():
    return jsonify({'link': f"{request.host_url}?ref={session['username']}"})

@app.route('/api/chat/messages', methods=['GET'])
def chat_messages():
    msgs = ChatMessage.query.order_by(ChatMessage.created_at.desc()).limit(50).all()
    return jsonify([{'username': m.username, 'message': m.message, 'time': m.created_at.isoformat()} for m in msgs[::-1]])

@app.route('/api/chat/send', methods=['POST'])
@login_required
def chat_send():
    data = request.json
    msg = data.get('message', '').strip()
    if not msg:
        return jsonify({'error': 'Empty'}), 400
    user = User.query.get(session['user_id'])
    cm = ChatMessage(user_id=user.id, username=user.username, message=msg[:500])
    db.session.add(cm)
    db.session.commit()
    return jsonify({'ok': True})

@app.route('/api/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username, 'balance': u.balance, 'is_admin': u.is_admin} for u in users])

@app.route('/api/admin/user_balance', methods=['POST'])
@admin_required
def admin_set_balance():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    if user:
        user.balance = float(data.get('balance', 0))
        db.session.commit()
        return jsonify({'ok': True})
    return jsonify({'error': 'User not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
