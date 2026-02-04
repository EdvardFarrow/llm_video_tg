#!/bin/bash

set -e

echo "⏳ Жду готовности базы данных..."
python -c "
import socket
import time
import os

host = os.getenv('DB_HOST', 'db')
port = int(os.getenv('DB_PORT', 5432))

while True:
    try:
        with socket.create_connection((host, port), timeout=2):
            break
    except OSError:
        print(f'Waiting for {host}:{port}...')
        time.sleep(2)
"
echo "✅ База данных доступна!"

echo "🚀 Запускаю загрузчик данных..."
python -m src.services.data_loader

echo "🤖 Запускаю бота..."
python -m src.bot.main