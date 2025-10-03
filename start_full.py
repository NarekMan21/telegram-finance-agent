#!/usr/bin/env python3
"""
Скрипт для запуска Telegram Financial Agent с режимом реального времени
"""

import os
import sys
import subprocess
import time
import webbrowser
import threading

def main():
    print("🚀 Telegram Financial Agent - Запуск в режиме реального времени")
    print("=" * 60)
    
    # Проверяем наличие необходимых файлов
    print("🔍 Проверка необходимых файлов...")
    
    required_files = [
        'app.py',
        'run_parser.py',
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
    
    # Запускаем компоненты в отдельных процессах
    print("🚀 Запуск компонентов...")
    print("📍 Веб-интерфейс будет доступен по адресу: http://localhost:8080")
    print("💡 Нажмите Ctrl+C для остановки всех компонентов")
    print("=" * 60)
    
    try:
        # Открываем браузер через 3 секунды
        def open_browser():
            time.sleep(3)
            webbrowser.open("http://localhost:8080")
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Запускаем веб-сервер в отдельном процессе
        print("🌐 Запуск веб-сервера...")
        server_process = subprocess.Popen([sys.executable, "app.py"])
        
        # Небольшая пауза перед запуском парсера
        time.sleep(2)
        
        # Запускаем парсер в режиме реального времени в отдельном процессе
        print("📡 Запуск парсера в режиме реального времени...")
        parser_process = subprocess.Popen([sys.executable, "run_parser.py"])
        
        print("\n✅ Все компоненты успешно запущены!")
        print("   - Веб-сервер: запущен")
        print("   - Парсер реального времени: запущен")
        print("\nДля остановки всех компонентов нажмите Ctrl+C\n")
        
        # Ждем завершения процессов
        try:
            server_process.wait()
            parser_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Остановка компонентов...")
            server_process.terminate()
            parser_process.terminate()
            server_process.wait()
            parser_process.wait()
            print("✅ Все компоненты остановлены")
            
    except Exception as e:
        print(f"❌ Ошибка при запуске компонентов: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Telegram Financial Agent в режиме реального времени успешно запущен!")
    else:
        print("\n❌ Возникли проблемы при запуске Telegram Financial Agent")
        sys.exit(1)