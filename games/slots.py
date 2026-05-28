import random
import json
from flask import jsonify, session
from models import db, User, Transaction, GameSession

SYMBOLS = [
    {"icon": "🍒", "fa": "fa-cherries", "value": 2, "prob": 20},
    {"icon": "🍋", "fa": "fa-lemon", "value": 3, "prob": 18},
    {"icon": "🍊", "fa": "fa-orange", "value": 4, "prob": 16},
    {"icon": "🍉", "fa": "fa-watermelon", "value": 5, "prob": 14},
    {"icon": "💎", "fa": "fa-gem", "value": 10, "prob": 8},
    {"icon": "7️⃣", "fa": "fa-7", "value": 20, "prob": 5},
    {"icon": "🐉", "fa": "fa-dragon", "value": 50, "prob": 2}
]

def generate_reel():
    return random.choices(SYMBOLS, weights=[s['prob'] for s in SYMBOLS])[0]

def generate_reels():
    return [[generate_reel() for _ in range(3)] for _ in range(5)]

def calculate_win(reels, bet):
    win = 0
    # 5 линий
    lines = [
        [(0,0),(1,0),(2,0),(3,0),(4,0)],
        [(0,1),(1,1),(2,1),(3,1),(4,1)],
        [(0,2),(1,2),(2,2),(3,2),(4,2)],
        [(0,0),(1,1),(2,2),(3,1),(4,0)],
        [(0,2),(1,1),(2,0),(3,1),(4,2)]
    ]
    for line in lines:
        first = reels[line[0][0]][line[0][1]]
        if all(reels[x][y]['icon'] == first['icon'] for x,y in line[1:]):
            win += bet * first['value']
    # Джекпот за 5 драконов в центре
    if all(reels[i][1]['icon'] == '🐉' for i in range(5)):
        win += 5000
    return win

def spin(data, user_id):
    bet = int(data.get('bet', 10))
    user = User.query.get(user_id)
    if user.balance < bet:
        return jsonify({'error': 'Недостаточно средств'}), 400
    # Спишем ставку (отдельный вызов place_bet не нужен, делаем здесь)
    user.balance -= bet
    db.session.commit()
    reels = generate_reels()
    win = calculate_win(reels, bet)
    if win > 0:
        user.balance += win
        db.session.commit()
    # Сохраняем сессию
    gs = GameSession(user_id=user_id, game='slots', bet=bet, win=win, result_data=json.dumps({'reels': [[s['icon'] for s in col] for col in reels]}))
    db.session.add(gs)
    db.session.commit()
    # Возвращаем данные для фронта с иконками
    reels_for_front = [[{'icon': s['icon'], 'fa': s['fa']} for s in col] for col in reels]
    return jsonify({'reels': reels_for_front, 'win': win, 'balance': user.balance})
