#!/usr/bin/env python3
"""
Финальный скрипт для установки зависимостей и запуска Telegram Financial Agent
"""

import os
import sys
import subprocess
import time
import shutil

def check_python():
    """Проверяем наличие Python"""
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True)
        print(f"✅ Python найден: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Python не найден: {e}")
        return False

def install_dependencies():
    """Устанавливаем зависимости"""
    print("🔄 Установка зависимостей...")
    
    # Создаем резервную копию requirements.txt если она существует
    if os.path.exists('requirements.txt'):
        shutil.copy('requirements.txt', 'requirements_backup.txt')
    
    # Создаем новый файл зависимостей
    dependencies = [
        "Flask==2.3.2",
        "Telethon==1.28.5",
        "requests==2.31.0",
        "python-dotenv==1.0.0"
    ]
    
    with open('requirements_new.txt', 'w') as f:
        for dep in dependencies:
            f.write(f"{dep}\n")
    
    try:
        # Пытаемся установить зависимости
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements_new.txt"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Зависимости успешно установлены")
            # Удаляем временный файл
            if os.path.exists('requirements_new.txt'):
                os.remove('requirements_new.txt')
            return True
        else:
            print(f"❌ Ошибка при установке зависимостей:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Таймаут при установке зависимостей")
        return False
    except Exception as e:
        print(f"❌ Ошибка при установке зависимостей: {e}")
        return False

def check_dependencies():
    """Проверяем наличие всех зависимостей"""
    print("🔍 Проверка установленных зависимостей...")
    
    dependencies = {
        'flask': 'Flask',
        'telethon': 'Telethon',
        'requests': 'requests'
    }
    
    missing = []
    
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {package} установлен")
        except ImportError:
            print(f"❌ {package} не установлен")
            missing.append(module)
    
    return len(missing) == 0

def main():
    print("🚀 Telegram Financial Agent - Установка и запуск")
    print("=" * 60)
    
    # Проверяем Python
    if not check_python():
        print("❌ Python не найден. Пожалуйста, установите Python 3.7 или выше")
        return False
    
    # Проверяем зависимости
    if not check_dependencies():
        print("🔄 Некоторые зависимости отсутствуют. Устанавливаю...")
        if not install_dependencies():
            print("❌ Не удалось установить зависимости")
            return False
        # Повторная проверка
        if not check_dependencies():
            print("❌ Не удалось установить все зависимости")
            return False
    
    print("\n🎉 Все готово для запуска Telegram Financial Agent!")
    print("\nДля запуска приложения выполните команду:")
    print("   python app.py")
    print("\nИли используйте один из созданных скриптов:")
    print("   start.bat    - для Windows")
    print("   python start.py - для всех систем")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Установка завершена успешно!")
    else:
        print("\n❌ Возникли проблемы при установке")
        sys.exit(1)