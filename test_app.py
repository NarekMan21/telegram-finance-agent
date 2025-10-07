#!/usr/bin/env python3
"""
Тестовое приложение для проверки функциональности Telegram Financial Agent
"""

import os
import json
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

# Проверим, существуют ли нужные файлы
def check_required_files():
    required_files = [
        'index.html',
        'main.js',
        'analytics.html',
        'settings.html',
        'transactions.html'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    return missing_files

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    print("🚀 Запуск тестового Telegram Financial Agent...")
    print("=" * 50)
    
    # Проверим наличие файлов
    missing = check_required_files()
    if missing:
        print(f"❌ Отсутствуют файлы: {missing}")
    else:
        print("✅ Все необходимые файлы найдены")
    
    # Запустим сервер
    print("📡 Сервер запущен на http://localhost:8080")
    print("💡 Нажмите Ctrl+C для остановки")
    app.run(host='0.0.0.0', port=8080, debug=True)