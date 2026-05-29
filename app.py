import os
import bcrypt
import secrets
import random
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Optional

# ---------- Конфигурация ----------
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cashx_ultimate_secret_2025')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///cashx_ultimate.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MIN_WITHDRAWAL = 1000

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# ---------- Модели ----------
class User(db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    balance: Mapped[float] = mapped_column(default=0.0)
    is_admin: Mapped[bool] = mapped_column(default=False)
    referrer_id: Mapped[Optional[int]] = mapped_column(db.ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'))
    amount: Mapped[float]
    type: Mapped[str]  # deposit, withdraw, bet, win
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'))
    username: Mapped[str]
    message: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

# ---------- Приложение ----------
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

# ---------- Декораторы ----------
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

# ---------- Страницы (HTML) ----------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/games')
def games():
    return render_template('games.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

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

# ---------- API авторизации ----------
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

# ---------- API для игр (реалистичные) ----------
@app.route('/api/slots/spin', methods=['POST'])
@login_required
def slots_spin():
    bet = request.json.get('bet', 10)
    symbols = ['🍒','🍋','🍊','🍉','💎','7️⃣','🐉']
    # Веса для генерации (вероятность дракона ниже, а популярных символов выше)
    weights = [30, 25, 20, 15, 8, 4, 2]  # чем больше число, тем чаще символ
    reels = []
    for _ in range(5):
        col = []
        for _ in range(3):
            sym = random.choices(symbols, weights=weights)[0]
            col.append(sym)
        reels.append(col)
    
    win = 0
    # Линии: верхняя (row=0), центральная (row=1), нижняя (row=2), две диагонали
    lines = [
        [(0,0),(1,0),(2,0),(3,0),(4,0)],  # верх
        [(0,1),(1,1),(2,1),(3,1),(4,1)],  # центр
        [(0,2),(1,2),(2,2),(3,2),(4,2)],  # низ
        [(0,0),(1,1),(2,2),(3,1),(4,0)],  # диагональ V
        [(0,2),(1,1),(2,0),(3,1),(4,2)]   # диагональ Λ
    ]
    
    # Стоимость символов
    payouts = {'🍒':2, '🍋':3, '🍊':4, '🍉':5, '💎':10, '7️⃣':20, '🐉':50}
    
    for line in lines:
        first_sym = reels[line[0][0]][line[0][1]]
        count = 1
        for (col, row) in line[1:]:
            if reels[col][row] == first_sym:
                count += 1
            else:
                break
        if count >= 3:
            win += bet * payouts.get(first_sym, 1) * (count - 2)
    
    # Джекпот за 5 драконов в центре
    center_line = [reels[i][1] for i in range(5)]
    if all(s == '🐉' for s in center_line):
        win += 5000
    
    user = User.query.get(session['user_id'])
    user.balance += win - bet
    db.session.commit()
    return jsonify({'reels': reels, 'win': win, 'balance': user.balance})

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
    # Сохраняем состояние в сессию (для раскрытия)
    session[f'mines_{session["user_id"]}'] = {'grid': grid, 'bet': bet, 'revealed': [], 'mines': mines}
    return jsonify({'grid': grid, 'bet': bet})

@app.route('/api/mines/reveal', methods=['POST'])
@login_required
def mines_reveal():
    row = request.json.get('row')
    col = request.json.get('col')
    game = session.get(f'mines_{session["user_id"]}')
    if not game:
        return jsonify({'error': 'No active game'}), 400
    cell = game['grid'][row][col]
    if cell == 1:
        # Мина – игра окончена
        session.pop(f'mines_{session["user_id"]}', None)
        return jsonify({'boom': True, 'win': 0})
    else:
        game['revealed'].append((row,col))
        multiplier = 1 + len(game['revealed']) * 0.2
        session[f'mines_{session["user_id"]}'] = game
        return jsonify({'boom': False, 'multiplier': round(multiplier,2)})

@app.route('/api/crash/start', methods=['POST'])
@login_required
def crash_start():
    bet = request.json.get('bet', 10)
    user = User.query.get(session['user_id'])
    if user.balance < bet:
        return jsonify({'error': 'Недостаточно средств'}), 400
    user.balance -= bet
    db.session.commit()
    session_id = secrets.token_urlsafe(16)
    # Для упрощения: в реальности краш-цикл управляется глобально, но здесь сделаем заглушку
    session[f'crash_{session_id}'] = {'user_id': session['user_id'], 'bet': bet, 'cashed_out': False}
    return jsonify({'session_id': session_id, 'balance': user.balance})

@app.route('/api/crash/cashout', methods=['POST'])
@login_required
def crash_cashout():
    session_id = request.json.get('session_id')
    crash = session.get(f'crash_{session_id}')
    if not crash or crash['cashed_out']:
        return jsonify({'error': 'Invalid session'}), 400
    multiplier = random.uniform(1.1, 5.0)
    win = int(crash['bet'] * multiplier)
    user = User.query.get(session['user_id'])
    user.balance += win
    db.session.commit()
    crash['cashed_out'] = True
    session[f'crash_{session_id}'] = crash
    return jsonify({'win': win, 'multiplier': round(multiplier,2), 'balance': user.balance})

@app.route('/api/crash/status', methods=['GET'])
def crash_status():
    # Для упрощения возвращаем растущий множитель
    import time
    fake_mult = 1.0 + (time.time() % 30) / 10
    return jsonify({'running': True, 'multiplier': round(fake_mult,2)})

@app.route('/api/dice/roll', methods=['POST'])
@login_required
def dice_roll():
    bet = request.json.get('bet', 10)
    prediction = request.json.get('prediction')
    target = request.json.get('target', 50)
    roll = random.randint(1,100)
    win = 0
    if prediction == 'under' and roll < target:
        win = int(bet * 1.98)
    elif prediction == 'over' and roll > target:
        win = int(bet * 1.98)
    elif prediction == 'number' and roll == target:
        win = bet * 50
    user = User.query.get(session['user_id'])
    if user.balance < bet:
        return jsonify({'error': 'Недостаточно средств'}), 400
    user.balance = user.balance - bet + win
    db.session.commit()
    return jsonify({'roll': roll, 'win': win, 'balance': user.balance})

@app.route('/api/coinflip/flip', methods=['POST'])
@login_required
def coinflip_flip():
    bet = request.json.get('bet', 10)
    choice = request.json.get('choice')
    result = random.choice(['heads', 'tails'])
    win = bet * 2 if choice == result else 0
    user = User.query.get(session['user_id'])
    if user.balance < bet:
        return jsonify({'error': 'Недостаточно средств'}), 400
    user.balance = user.balance - bet + win
    db.session.commit()
    return jsonify({'result': result, 'win': win, 'balance': user.balance})

@app.route('/api/keno/draw', methods=['POST'])
@login_required
def keno_draw():
    bet = request.json.get('bet', 10)
    picks = request.json.get('picks', [])
    drawn = random.sample(range(1,81), 20)
    matches = len(set(picks) & set(drawn))
    win = matches * (bet // 10) * 2
    user = User.query.get(session['user_id'])
    if user.balance < bet:
        return jsonify({'error': 'Недостаточно средств'}), 400
    user.balance = user.balance - bet + win
    db.session.commit()
    return jsonify({'drawn': drawn, 'matches': matches, 'win': win, 'balance': user.balance})

@app.route('/api/boomcity/spin', methods=['POST'])
@login_required
def boomcity_spin():
    bet = request.json.get('bet', 10)
    win = random.choice([0, bet, bet*2, bet*5, bet*10])
    user = User.query.get(session['user_id'])
    if user.balance < bet:
        return jsonify({'error': 'Недостаточно средств'}), 400
    user.balance = user.balance - bet + win
    db.session.commit()
    return jsonify({'win': win, 'balance': user.balance})

@app.route('/api/provider_games')
def get_provider_games():
    games = ProviderGame.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': g.id,
        'name': g.name,
        'provider': g.provider,
        'iframe_url': g.iframe_url
    } for g in games])

@app.route('/provider_games')
def provider_games():
    return render_template('provider_games.html')

@app.route('/play/provider/<int:game_id>')
@login_required
def play_provider_game(game_id):
    game = ProviderGame.query.get_or_404(game_id)
    return render_template('play_provider_game.html', game=game)

# ---------- Дополнительные API (бонусы, рефералы, чат, админка) ----------
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

@app.route('/api/admin/add_provider_game', methods=['POST'])
@admin_required
def add_provider_game():
    data = request.json
    name = data.get('name')
    provider = data.get('provider')
    iframe_url = data.get('iframe_url')
    if not name or not provider or not iframe_url:
        return jsonify({'error': 'Missing fields'}), 400
    game = ProviderGame(name=name, provider=provider, iframe_url=iframe_url)
    db.session.add(game)
    db.session.commit()
    return jsonify({'ok': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
