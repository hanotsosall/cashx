import random
import threading
import time
import json
from flask import jsonify, session as fl_session
from models import db, User, GameSession

# Глобальное состояние краша
crash_state = {
    'running': False,
    'multiplier': 1.0,
    'start_time': 0,
    'crash_point': 0,
    'bets': {}  # user_id -> {'bet': float, 'cashed_out': bool, 'session_id': str}
}

def start_round():
    global crash_state
    if crash_state['running']:
        return
    crash_state['running'] = True
    crash_state['multiplier'] = 1.0
    crash_state['start_time'] = time.time()
    # Случайная точка краша от 1.1 до 100 с распределением
    crash_state['crash_point'] = round(random.uniform(1.1, 100), 2)
    # Запускаем таймер обновления
    def update_multiplier():
        while crash_state['running']:
            elapsed = time.time() - crash_state['start_time']
            # Экспоненциальный рост
            multiplier = 1.0 + elapsed * 1.5
            if multiplier >= crash_state['crash_point']:
                # Краш!
                crash_state['running'] = False
                # Все невышедшие ставки проиграны
                for uid, bet_info in crash_state['bets'].items():
                    if not bet_info['cashed_out']:
                        pass  # ставка уже списана, ничего не возвращаем
                crash_state['bets'].clear()
                break
            crash_state['multiplier'] = multiplier
            time.sleep(0.1)
    threading.Thread(target=update_multiplier, daemon=True).start()

def get_status():
    return jsonify({
        'running': crash_state['running'],
        'multiplier': round(crash_state['multiplier'], 2),
        'crash_point': crash_state['crash_point'] if not crash_state['running'] else None
    })

def start(data, user_id):
    bet = float(data.get('bet', 10))
    user = User.query.get(user_id)
    if user.balance < bet:
        return jsonify({'error': 'Недостаточно средств'}), 400
    if not crash_state['running']:
        start_round()
    # Списываем ставку
    user.balance -= bet
    db.session.commit()
    session_id = f"{user_id}_{int(time.time())}"
    crash_state['bets'][user_id] = {'bet': bet, 'cashed_out': False, 'session_id': session_id}
    fl_session['crash_session'] = session_id
    return jsonify({'ok': True, 'balance': user.balance, 'session_id': session_id})

def cashout(data, user_id):
    session_id = data.get('session_id')
    if user_id not in crash_state['bets'] or crash_state['bets'][user_id]['session_id'] != session_id:
        return jsonify({'error': 'Invalid session'}), 400
    if crash_state['bets'][user_id]['cashed_out']:
        return jsonify({'error': 'Already cashed out'}), 400
    if not crash_state['running']:
        return jsonify({'error': 'Game crashed'}), 400
    multiplier = crash_state['multiplier']
    bet = crash_state['bets'][user_id]['bet']
    win = bet * multiplier
    crash_state['bets'][user_id]['cashed_out'] = True
    user = User.query.get(user_id)
    user.balance += win
    db.session.commit()
    # Логируем
    gs = GameSession(user_id=user_id, game='crash', bet=bet, win=win, result_data=json.dumps({'multiplier': multiplier}))
    db.session.add(gs)
    db.session.commit()
    return jsonify({'win': win, 'balance': user.balance, 'multiplier': multiplier})
