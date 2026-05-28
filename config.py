import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ultimate-cashx-secret-key-2025')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///cashx_ultimate.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MIN_WITHDRAWAL = 1000   # минимальный вывод в рублях
    # Платёжные ключи (заглушки)
    STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', '')
    COINPAYMENTS_API_KEY = os.environ.get('COINPAYMENTS_API_KEY', '')
