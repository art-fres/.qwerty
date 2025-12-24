import sys
import os
from flask import Flask, request, jsonify
import asyncio
import threading
import logging
import time

# Добавляем путь к проекту
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

from main import bot, dp, set_webhook_sync, logger
from aiogram.types import Update

app = Flask(__name__)

# Настройка логгера
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# Глобальный event loop для всего приложения
_loop = None
_loop_thread = None

def get_or_create_loop():
    """Создает или возвращает существующий event loop"""
    global _loop, _loop_thread

    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()

        # Запускаем loop в отдельном потоке
        def run_loop():
            asyncio.set_event_loop(_loop)
            _loop.run_forever()

        _loop_thread = threading.Thread(target=run_loop, daemon=True)
        _loop_thread.start()
        logger.info("Event loop создан и запущен")

    return _loop

@app.route('/webhook', methods=['POST'])
def webhook():

    try:
        update_data = request.json
        update = Update(**update_data)


        loop = get_or_create_loop()


        future = asyncio.run_coroutine_threadsafe(
            dp.feed_update(bot, update),
            loop
        )



        return jsonify({'status': 'ok'})

    except Exception as e:
        logger.error(f"Ошибка в webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/')
def home():
    return "🤖 Бот работает (исправленный event loop)"

@app.route('/set_webhook')
def set_webhook():

    try:
        if set_webhook_sync():
            return "✅ Webhook установлен"
        return "❌ Ошибка установки"
    except Exception as e:
        return f"❌ {e}"


def setup_on_start():
    time.sleep(5)
    logger.info("Устанавливаю вебхук...")
    try:
        set_webhook_sync()
    except Exception as e:
        logger.error(f"Ошибка установки вебхука: {e}")


threading.Thread(target=setup_on_start, daemon=True).start()


import atexit

@atexit.register
def cleanup():
    if _loop and not _loop.is_closed():
        _loop.call_soon_threadsafe(_loop.stop)
        logger.info("Event loop остановлен")