import random
from flask import jsonify
from models import db, User, GameSession

def roll(data, user_id):
    bet = float(data.get('bet', 10))
    prediction = data.get('prediction')  # 'under', 'over', 'number'
    target = int(data.get('target', 50))
    user = User.query.get(user_id)
    if user.balance < bet:
        return jsonify({'error': 'Недостаточно средств'}), 400
    roll = random.randint(1, 100)
    win = 0
    if prediction == 'under' and roll < target:
        win = bet * 1.98
    elif prediction == 'over' and roll > target:
        win = bet * 1.98
    elif prediction == 'number' and roll == target:
        win = bet * 50
    # Списываем ставку, начисляем выигрыш
    user.balance -= bet
    if win > 0:
        user.balance += win
    db.session.commit()
    gs = GameSession(user_id=user_id, game='dice', bet=bet, win=win, result_data={'roll': roll})
    db.session.add(gs)
    db.session.commit()
    return jsonify({'roll': roll, 'win': win, 'balance': user.balance})
