import random
import json
from flask import jsonify
from models import db, User, GameSession

def generate_grid(mines_count):
    grid = [[0]*5 for _ in range(5)]  # 0 - безопасно, 1 - мина
    positions = [(i,j) for i in range(5) for j in range(5)]
    for _ in range(mines_count):
        r,c = random.choice(positions)
        grid[r][c] = 1
        positions.remove((r,c))
    return grid

def generate(data, user_id):
    mines = int(data.get('mines', 3))
    bet = int(data.get('bet', 10))
    user = User.query.get(user_id)
    if user.balance < bet:
        return jsonify({'error': 'Недостаточно средств'}), 400
    user.balance -= bet
    db.session.commit()
    grid = generate_grid(mines)
    # Сохраняем сессию в памяти или БД
    session_key = f'mines_{user_id}'
    from flask import session as fl_session
    fl_session[session_key] = {'grid': grid, 'bet': bet, 'revealed': [], 'mines': mines}
    return jsonify({'grid': grid, 'bet': bet, 'balance': user.balance})

def reveal(data, user_id):
    row = data.get('row')
    col = data.get('col')
    from flask import session as fl_session
    session_key = f'mines_{user_id}'
    game = fl_session.get(session_key)
    if not game:
        return jsonify({'error': 'No active game'}), 400
    cell = game['grid'][row][col]
    if cell == 1:
        # Мина – игра окончена, ставка потеряна
        del fl_session[session_key]
        return jsonify({'boom': True, 'win': 0})
    else:
        # Безопасная клетка
        game['revealed'].append((row,col))
        # Расчёт множителя (упрощённо)
        multiplier = 1 + len(game['revealed']) * 0.2
        win = int(game['bet'] * multiplier)
        fl_session[session_key] = game
        return jsonify({'boom': False, 'win': win, 'multiplier': multiplier})
