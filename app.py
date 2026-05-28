import os
import bcrypt
import secrets
import json
import random
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, g
from config import Config
from models import db, User, Transaction, WithdrawRequest, GameSession, ChatMessage
from games import slots, mines, crash, dice, coinflip, keno, boomcity
from payments import crypto, fiat
from flask import redirect, url_for

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()
    # создать админа если нет
    if not User.query.filter_by(username='admin').first():
        hashed = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
        admin = User(username='admin', password=hashed, is_admin=True, balance=1000000)
        db.session.add(admin)
        db.session.commit()

def login_required_page(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))  # редирект на главную (где форма входа)
        return f(*args, **kwargs)
    return decorated


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

@app.route('/profile')
@login_required_page
def profile():
    return render_template('profile.html')

@app.route('/admin')
@login_required_page
def admin_panel():
    return render_template('admin.html')

@app.route('/game/<game_name>')
@login_required_page
def game_page(game_name):
    if game_name in ['slots', 'mines', 'crash', 'dice', 'coinflip', 'keno', 'boomcity']:
        return render_template(f'game_{game_name}.html')
    return "Game not found", 404

# ---------- API Авторизации ----------
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
    return jsonify({'ok': True, 'user': {'id': user.id, 'username': user.username, 'balance': user.balance}})

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
@login_required
def get_user():
    user = User.query.get(session['user_id'])
    return jsonify({'id': user.id, 'username': user.username, 'balance': user.balance})

# ---------- API Баланса и транзакций ----------
@app.route('/api/balance')
@login_required
def get_balance():
    user = User.query.get(session['user_id'])
    return jsonify({'balance': user.balance})

@app.route('/api/update_balance', methods=['POST'])
@login_required
def update_balance():
    data = request.json
    delta = data.get('delta', 0)
    user = User.query.get(session['user_id'])
    user.balance += delta
    db.session.commit()
    return jsonify({'balance': user.balance})

# ---------- Платёжные заглушки (реальные деньги) ----------
@app.route('/api/deposit', methods=['POST'])
@login_required
def deposit():
    data = request.json
    amount = float(data.get('amount', 0))
    method = data.get('method')  # 'crypto' or 'card'
    if amount <= 0:
        return jsonify({'error': 'Сумма должна быть >0'}), 400
    # Здесь интеграция с реальным платёжным шлюзом (Stripe/CoinPayments)
    # Для демо просто добавляем баланс
    user = User.query.get(session['user_id'])
    user.balance += amount
    tx = Transaction(user_id=user.id, amount=amount, currency='RUB', type='deposit', status='completed')
    db.session.add(tx)
    db.session.commit()
    return jsonify({'ok': True, 'balance': user.balance, 'tx_id': tx.id})

@app.route('/api/withdraw', methods=['POST'])
@login_required
def withdraw():
    data = request.json
    amount = float(data.get('amount', 0))
    method = data.get('method')  # 'crypto' or 'card'
    address = data.get('address', '')
    if amount < Config.MIN_WITHDRAWAL:
        return jsonify({'error': f'Минимальный вывод {Config.MIN_WITHDRAWAL} RUB'}), 400
    user = User.query.get(session['user_id'])
    if user.balance < amount:
        return jsonify({'error': 'Недостаточно средств'}), 400
    user.balance -= amount
    req = WithdrawRequest(user_id=user.id, amount=amount, method=method, address=address, status='pending')
    db.session.add(req)
    db.session.commit()
    return jsonify({'ok': True, 'request_id': req.id})

# ---------- API для игр (общий обработчик ставок) ----------
@app.route('/api/place_bet', methods=['POST'])
@login_required
def place_bet():
    data = request.json
    bet = float(data.get('bet', 0))
    win = float(data.get('win', 0))
    game_name = data.get('game', 'unknown')
    user = User.query.get(session['user_id'])
    if bet > 0 and user.balance < bet:
        return jsonify({'error': 'Недостаточно средств'}), 400
    # Списываем ставку
    if bet > 0:
        user.balance -= bet
        tx = Transaction(user_id=user.id, amount=-bet, type='bet', status='completed')
        db.session.add(tx)
    # Начисляем выигрыш
    if win > 0:
        user.balance += win
        tx2 = Transaction(user_id=user.id, amount=win, type='win', status='completed')
        db.session.add(tx2)
    # Логируем сессию
    gs = GameSession(user_id=user.id, game=game_name, bet=bet, win=win, result_data=json.dumps(data.get('result', {})))
    db.session.add(gs)
    db.session.commit()
    return jsonify({'balance': user.balance})

# ---------- Специфические игровые API (слоты, mines, crash...) ----------
# Они вынесены в модули games, здесь только импорт и вызов

@app.route('/api/slots/spin', methods=['POST'])
@login_required
def slots_spin():
    return slots.spin(request.json, session['user_id'])

@app.route('/api/mines/generate', methods=['POST'])
@login_required
def mines_generate():
    return mines.generate(request.json, session['user_id'])

@app.route('/api/mines/reveal', methods=['POST'])
@login_required
def mines_reveal():
    return mines.reveal(request.json, session['user_id'])

@app.route('/api/crash/start', methods=['POST'])
@login_required
def crash_start():
    return crash.start(request.json, session['user_id'])

@app.route('/api/crash/cashout', methods=['POST'])
@login_required
def crash_cashout():
    return crash.cashout(request.json, session['user_id'])

@app.route('/api/crash/status', methods=['GET'])
def crash_status():
    return crash.get_status()

@app.route('/api/dice/roll', methods=['POST'])
@login_required
def dice_roll():
    return dice.roll(request.json, session['user_id'])

@app.route('/api/coinflip/flip', methods=['POST'])
@login_required
def coinflip_flip():
    return coinflip.flip(request.json, session['user_id'])

@app.route('/api/keno/draw', methods=['POST'])
@login_required
def keno_draw():
    return keno.draw(request.json, session['user_id'])

@app.route('/api/boomcity/spin', methods=['POST'])
@login_required
def boomcity_spin():
    return boomcity.spin(request.json, session['user_id'])

# ---------- Чат ----------
@app.route('/api/chat/messages', methods=['GET'])
def get_chat_messages():
    messages = ChatMessage.query.order_by(ChatMessage.created_at.desc()).limit(50).all()
    return jsonify([{'username': m.username, 'message': m.message, 'time': m.created_at.isoformat()} for m in messages[::-1]])

@app.route('/api/chat/send', methods=['POST'])
@login_required
def send_chat_message():
    data = request.json
    msg = data.get('message', '').strip()
    if not msg:
        return jsonify({'error': 'Пустое сообщение'}), 400
    user = User.query.get(session['user_id'])
    cm = ChatMessage(user_id=user.id, username=user.username, message=msg[:500])
    db.session.add(cm)
    db.session.commit()
    return jsonify({'ok': True})

# ---------- Админка ----------
@app.route('/api/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username, 'balance': u.balance, 'is_admin': u.is_admin} for u in users])

@app.route('/api/admin/user_balance', methods=['POST'])
@admin_required
def admin_set_balance():
    data = request.json
    user_id = data.get('user_id')
    new_balance = float(data.get('balance', 0))
    user = User.query.get(user_id)
    if user:
        user.balance = new_balance
        db.session.commit()
        return jsonify({'ok': True})
    return jsonify({'error': 'User not found'}), 404

# Удаление пользователя (только для админа)
@app.route('/api/admin/user/<int:user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'ok': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
