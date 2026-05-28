import random
from flask import jsonify
from models import db, User, GameSession

def flip(data, user_id):
    bet = int(data.get('bet', 10))
    choice = data.get('choice')  # 'heads' or 'tails'
    user = User.query.get(user_id)
    if user.balance < bet:
        return jsonify({'error': 'Недостаточно средств'}), 400
    result = random.choice(['heads', 'tails'])
    win = 0
    if choice == result:
        win = bet * 2
    # Списываем ставку и начисляем выигрыш
    user.balance -= bet
    if win > 0:
        user.balance += win
    db.session.commit()
    # Логируем сессию
    gs = GameSession(user_id=user_id, game='coinflip', bet=bet, win=win, result_data={'choice': choice, 'result': result})
    db.session.add(gs)
    db.session.commit()
    return jsonify({'result': result, 'win': win, 'balance': user.balance})
