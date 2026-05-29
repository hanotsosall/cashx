from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Float, default=0.0)          # только реальные деньги
    # Нет бонусного баланса – убрали
    is_admin = db.Column(db.Boolean, default=False)
    referrer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    # Платёжные данные
    crypto_wallet = db.Column(db.String(200), nullable=True)
    bank_card = db.Column(db.String(20), nullable=True)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    amount = db.Column(db.Float)
    currency = db.Column(db.String(10), default='RUB')
    type = db.Column(db.String(20))  # deposit, withdraw, bet, win
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    external_id = db.Column(db.String(100))  # ID платежа в системе
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WithdrawRequest(db.Model):
    __tablename__ = 'withdraw_requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    amount = db.Column(db.Float)
    method = db.Column(db.String(20))  # crypto, card
    address = db.Column(db.String(200))  # кошелёк или номер карты
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GameSession(db.Model):
    __tablename__ = 'game_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    game = db.Column(db.String(50))
    bet = db.Column(db.Float)
    win = db.Column(db.Float)
    result_data = db.Column(db.Text)  # JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    username = db.Column(db.String(80))
    message = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProviderGame(db.Model):
    __tablename__ = 'provider_games'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    provider = db.Column(db.String(50), nullable=False)  # Pragmatic, NetEnt и т.д.
    iframe_url = db.Column(db.String(500), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
