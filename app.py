import os
import bcrypt
import secrets
import string
import random
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, g
from config import Config
from db import get_db, init_db

app = Flask(__name__)
app.config.from_object(Config)

with app.app_context():
    init_db()

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
        db = get_db()
        user = db.execute("SELECT is_admin FROM users WHERE id=?", (session['user_id'],)).fetchone()
        if not user or not user['is_admin']:
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
@login_required
def profile():
    return render_template('profile.html')

@app.route('/admin')
@admin_required
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
    db = get_db()
    if db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone():
        return jsonify({'error': 'Имя занято'}), 400
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    referrer_id = None
    if ref:
        ref_user = db.execute("SELECT id FROM users WHERE username=?", (ref,)).fetchone()
        if ref_user:
            referrer_id = ref_user['id']
    db.execute("INSERT INTO users (username, password, bonus_balance, referrer_id) VALUES (?,?,?,?)",
               (username, hashed, Config.BONUS_ON_REGISTER, referrer_id))
    db.commit()
    user = db.execute("SELECT id, username, balance, bonus_balance FROM users WHERE username=?", (username,)).fetchone()
    session['user_id'] = user['id']
    session['username'] = user['username']
    return jsonify({'ok': True, 'user': dict(user)})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    db = get_db()
    user = db.execute("SELECT id, username, password, balance, bonus_balance, is_admin FROM users WHERE username=?", (username,)).fetchone()
    if not user or not bcrypt.checkpw(password.encode(), user['password'].encode()):
        return jsonify({'error': 'Неверные данные'}), 401
    session['user_id'] = user['id']
    session['username'] = user['username']
    return jsonify({'ok': True, 'user': dict(user)})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'ok': True})

@app.route('/api/user')
@login_required
def get_user():
    db = get_db()
    user = db.execute("SELECT id, username, balance, bonus_balance FROM users WHERE id=?", (session['user_id'],)).fetchone()
    return jsonify(dict(user))

@app.route('/api/balance')
@login_required
def get_balance():
    db = get_db()
    user = db.execute("SELECT balance, bonus_balance FROM users WHERE id=?", (session['user_id'],)).fetchone()
    return jsonify({'balance': user['balance'], 'bonus_balance': user['bonus_balance']})

@app.route('/api/place_bet', methods=['POST'])
@login_required
def place_bet():
    data = request.json
    bet = int(data.get('bet', 0))
    win = int(data.get('win', 0))
    db = get_db()
    user = db.execute("SELECT balance, bonus_balance FROM users WHERE id=?", (session['user_id'],)).fetchone()
    total = user['balance'] + user['bonus_balance']
    if total < bet:
        return jsonify({'error': 'Недостаточно средств'}), 400
    from_bonus = min(user['bonus_balance'], bet)
    from_main = bet - from_bonus
    db.execute("UPDATE users SET balance = balance - ?, bonus_balance = bonus_balance - ? WHERE id=?", (from_main, from_bonus, session['user_id']))
    if win > 0:
        db.execute("UPDATE users SET balance = balance + ? WHERE id=?", (win, session['user_id']))
    db.commit()
    new_user = db.execute("SELECT balance, bonus_balance FROM users WHERE id=?", (session['user_id'],)).fetchone()
    return jsonify({'balance': new_user['balance'], 'bonus_balance': new_user['bonus_balance']})

# ---------- Логика игр ----------
@app.route('/api/slots/spin', methods=['POST'])
@login_required
def slots_spin():
    bet = int(request.json.get('bet', 10))
    # Простая слото-машина (3x5, эмодзи)
    symbols = ['🍒', '🍋', '🍊', '🍉', '💎', '7️⃣', '🐉']
    reels = [[random.choice(symbols) for _ in range(3)] for _ in range(5)]
    # расчёт выигрыша (примитивный, для красоты)
    win = 0
    for row in range(3):
        if reels[0][row] == reels[1][row] == reels[2][row] == reels[3][row] == reels[4][row]:
            mult = {'🍒':2, '🍋':3, '🍊':4, '🍉':5, '💎':10, '7️⃣':20, '🐉':50}.get(reels[0][row], 1)
            win += bet * mult
    # Джекпот 5 драконов
    if all(reels[i][1] == '🐉' for i in range(5)):
        win += 5000
    # вызываем API ставки
    return jsonify({'reels': reels, 'win': win})

@app.route('/api/mines/generate', methods=['POST'])
@login_required
def mines_generate():
    mines = int(request.json.get('mines', 3))
    grid = [[0]*5 for _ in range(5)]
    positions = [(i,j) for i in range(5) for j in range(5)]
    for _ in range(mines):
        r,c = random.choice(positions)
        grid[r][c] = 1  # мина
        positions.remove((r,c))
    return jsonify({'grid': grid})

@app.route('/api/crash/round', methods=['GET'])
def crash_round():
    # Симуляция множителя краша
    multiplier = round(random.uniform(1.01, 100), 2)
    return jsonify({'multiplier': multiplier})

@app.route('/api/dice/roll', methods=['POST'])
@login_required
def dice_roll():
    roll = random.randint(1, 100)
    return jsonify({'roll': roll})

@app.route('/api/coinflip/flip', methods=['POST'])
@login_required
def coinflip_flip():
    result = random.choice(['heads', 'tails'])
    return jsonify({'result': result})

@app.route('/api/keno/draw', methods=['POST'])
@login_required
def keno_draw():
    picks = request.json.get('picks', [])
    drawn = random.sample(range(1, 81), 20)
    matches = len(set(picks) & set(drawn))
    win = matches * 10  # простая формула
    return jsonify({'drawn': drawn, 'matches': matches, 'win': win})

@app.route('/api/boomcity/spin', methods=['POST'])
@login_required
def boomcity_spin():
    # Простая имитация взрыва
    win = random.choice([0, random.randint(50, 500)])
    return jsonify({'win': win})

# ---------- Бонус-коды ----------
@app.route('/api/bonus/apply', methods=['POST'])
@login_required
def apply_bonus():
    data = request.json
    code = data.get('code', '').upper()
    db = get_db()
    bonus = db.execute("SELECT id, amount, expires_at FROM bonus_codes WHERE code=? AND used_by IS NULL", (code,)).fetchone()
    if not bonus:
        return jsonify({'error': 'Неверный код'}), 400
    if datetime.now() > datetime.fromisoformat(bonus['expires_at']):
        return jsonify({'error': 'Код истёк'}), 400
    db.execute("UPDATE bonus_codes SET used_by=? WHERE id=?", (session['user_id'], bonus['id']))
    db.execute("UPDATE users SET bonus_balance = bonus_balance + ? WHERE id=?", (bonus['amount'], session['user_id']))
    db.commit()
    return jsonify({'ok': True, 'amount': bonus['amount']})

# ---------- Рефералка ----------
@app.route('/api/referral/link')
@login_required
def referral_link():
    return jsonify({'link': f"{request.host_url}?ref={session['username']}"})

@app.route('/api/referral/stats')
@login_required
def referral_stats():
    db = get_db()
    count = db.execute("SELECT COUNT(*) as cnt FROM users WHERE referrer_id=?", (session['user_id'],)).fetchone()['cnt']
    earnings = db.execute("SELECT SUM(commission) as sum FROM referrals WHERE referrer_id=?", (session['user_id'],)).fetchone()['sum'] or 0
    return jsonify({'count': count, 'earnings': earnings})

# ---------- Чат ----------
@app.route('/api/chat/messages', methods=['GET'])
def chat_messages():
    db = get_db()
    msgs = db.execute("SELECT username, message, created_at FROM chat_messages ORDER BY id DESC LIMIT 50").fetchall()
    return jsonify([dict(m) for m in msgs][::-1])

@app.route('/api/chat/send', methods=['POST'])
@login_required
def chat_send():
    data = request.json
    msg = data.get('message', '').strip()
    if not msg:
        return jsonify({'error': 'Empty'}), 400
    db = get_db()
    db.execute("INSERT INTO chat_messages (user_id, username, message) VALUES (?,?,?)", (session['user_id'], session['username'], msg[:200]))
    db.commit()
    return jsonify({'ok': True})

# ---------- Админка ----------
@app.route('/api/admin/users')
@admin_required
def admin_users():
    db = get_db()
    users = db.execute("SELECT id, username, balance, bonus_balance, is_admin FROM users").fetchall()
    return jsonify([dict(u) for u in users])

@app.route('/api/admin/bonus', methods=['POST'])
@admin_required
def admin_give_bonus():
    data = request.json
    username = data.get('username')
    amount = int(data.get('amount', 0))
    db = get_db()
    db.execute("UPDATE users SET bonus_balance = bonus_balance + ? WHERE username=?", (amount, username))
    db.commit()
    return jsonify({'ok': True})

@app.route('/api/admin/generate_code', methods=['POST'])
@admin_required
def admin_gen_code():
    code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
    amount = int(request.json.get('amount', 100))
    expires = datetime.now() + timedelta(days=7)
    db = get_db()
    db.execute("INSERT INTO bonus_codes (code, amount, expires_at) VALUES (?,?,?)", (code, amount, expires.isoformat()))
    db.commit()
    return jsonify({'code': code})

@app.route('/api/admin/games', methods=['GET'])
@admin_required
def admin_get_games():
    db = get_db()
    games = db.execute("SELECT * FROM external_games").fetchall()
    return jsonify([dict(g) for g in games])

@app.route('/api/admin/games', methods=['POST'])
@admin_required
def admin_add_game():
    data = request.json
    name = data.get('name')
    iframe_url = data.get('iframe_url')
    min_bet = data.get('min_bet', 1)
    db = get_db()
    db.execute("INSERT INTO external_games (name, iframe_url, min_bet) VALUES (?,?,?)", (name, iframe_url, min_bet))
    db.commit()
    return jsonify({'ok': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
