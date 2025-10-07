#!/usr/bin/env python3
"""
Финальный скрипт для запуска Telegram Financial Agent
"""

import os
import sys
import subprocess
import time
import webbrowser

def main():
    print("🚀 Telegram Financial Agent - Запуск")
    print("=" * 50)
    
    # Проверяем наличие необходимых файлов
    print("🔍 Проверка необходимых файлов...")
    
    required_files = [
        'app.py',
        'config.json',
        'index.html',
        'main.js'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Отсутствуют файлы: {missing_files}")
        return False
    
    print("✅ Все необходимые файлы найдены")
    
    # Проверяем зависимости
    print("🔍 Проверка зависимостей...")
    try:
        import flask
        import telethon
        print("✅ Все зависимости установлены")
    except ImportError:
        print("🔄 Установка зависимостей...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True, capture_output=True)
            print("✅ Зависимости успешно установлены")
        except subprocess.CalledProcessError:
            print("❌ Ошибка при установке зависимостей")
            return False
    
    # Запускаем сервер
    print("🚀 Запуск веб-сервера...")
    print("📍 Сервер будет доступен по адресу: http://localhost:8080")
    print("💡 Нажмите Ctrl+C для остановки сервера")
    print("=" * 50)
    
    try:
        # Открываем браузер через 2 секунды
        import threading
        def open_browser():
            time.sleep(2)
            webbrowser.open("http://localhost:8080")
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Запускаем Flask приложение
        os.system("python app.py")
        
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка при запуске сервера: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Telegram Financial Agent успешно запущен!")
    else:
        print("\n❌ Возникли проблемы при запуске Telegram Financial Agent")
        sys.exit(1)