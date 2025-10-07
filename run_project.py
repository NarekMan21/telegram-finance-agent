#!/usr/bin/env python3
"""
Скрипт для запуска Telegram Financial Agent
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """Проверяем наличие необходимых зависимостей"""
    try:
        import flask
        import telethon
        print("✅ Все необходимые зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        return False

def start_server():
    """Запускаем веб-сервер"""
    print("🚀 Запуск Telegram Financial Agent...")
    print("=" * 50)
    
    # Проверяем конфигурацию
    if not os.path.exists('config.json'):
        print("❌ Файл config.json не найден!")
        return False
    
    # Проверяем наличие веб-файлов
    required_files = ['index.html', 'main.js']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Файл {file} не найден!")
            return False
    
    print("✅ Все файлы на месте")
    print("📡 Сервер будет доступен по адресу: http://localhost:8080")
    print("💡 Нажмите Ctrl+C для остановки сервера")
    print("=" * 50)
    
    # Запускаем сервер
    try:
        # Пробуем запустить основное приложение
        os.system("python app.py")
        return True
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем")
        return True
    except Exception as e:
        print(f"❌ Ошибка при запуске сервера: {e}")
        return False

def main():
    print("🤖 Telegram Financial Agent - Скрипт запуска")
    print("=" * 50)
    
    # Проверяем зависимости
    if not check_dependencies():
        print("🔄 Установка зависимостей...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Запускаем сервер
    start_server()

if __name__ == "__main__":
    main()