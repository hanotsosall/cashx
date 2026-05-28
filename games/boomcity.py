import random
from flask import jsonify
from models import db, User, GameSession

def spin(data, user_id):
    bet = int(data.get('bet', 10))
    user = User.query.get(user_id)
    if user.balance < bet:
        return jsonify({'error': 'Недостаточно средств'}), 400
    # Случайный выигрыш от 0 до x5
    win = random.choice([0, bet, bet*2, bet*5])
    user.balance -= bet
    if win > 0:
        user.balance += win
    db.session.commit()
    gs = GameSession(user_id=user_id, game='boomcity', bet=bet, win=win)
    db.session.add(gs)
    db.session.commit()
    return jsonify({'win': win, 'balance': user.balance})
