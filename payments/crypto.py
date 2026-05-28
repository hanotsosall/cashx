# Заглушка для криптовалютных платежей
def process_crypto_payment(amount, currency='USDT'):
    # В реальном проекте здесь был бы вызов API CoinPayments, Binance Pay и т.д.
    # Для демо просто возвращаем успех
    return {'success': True, 'transaction_id': 'demo_crypto_123', 'amount': amount}

def check_crypto_status(tx_id):
    return {'status': 'completed'}
