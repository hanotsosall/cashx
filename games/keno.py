import random
from flask import jsonify
from models import db, User, GameSession

def draw(data, user_id):
    bet = int(data.get('bet', 10))
    picks = data.get('picks', [])  # список выбранных чисел от 1 до 80
    user = User.query.get(user_id)
    if user.balance < bet:
        return jsonify({'error': 'Недостаточно средств'}), 400
    drawn = random.sample(range(1, 81), 20)
    matches = len(set(picks) & set(drawn))
    win = matches * (bet // 10) * 2  # простой коэффициент
    user.balance -= bet
    if win > 0:
        user.balance += win
    db.session.commit()
    gs = GameSession(user_id=user_id, game='keno', bet=bet, win=win, result_data={'picks': picks, 'drawn': drawn})
    db.session.add(gs)
    db.session.commit()
    return jsonify({'drawn': drawn, 'matches': matches, 'win': win, 'balance': user.balance})
