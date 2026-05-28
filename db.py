import sqlite3
from flask import g

DATABASE = 'cashx.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    from flask import current_app
    with current_app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            balance INTEGER DEFAULT 0,
            bonus_balance INTEGER DEFAULT 0,
            referrer_id INTEGER,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS bonus_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            amount INTEGER,
            used_by INTEGER,
            expires_at TIMESTAMP
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS external_games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            iframe_url TEXT,
            min_bet INTEGER,
            is_active BOOLEAN DEFAULT 1
        )''')
        db.commit()
        admin = cursor.execute("SELECT * FROM users WHERE username='admin'").fetchone()
        if not admin:
            import bcrypt
            hashed = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
            cursor.execute("INSERT INTO users (username, password, is_admin, balance) VALUES (?,?,?,?)",
                           ('admin', hashed, 1, 1000000))
            db.commit()
