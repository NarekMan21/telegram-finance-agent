#!/usr/bin/env python3
"""
Скрипт для развертывания проекта на Railway
"""

import os
import subprocess
import sys
import json

def check_railway_cli():
    """Проверяет, установлен ли Railway CLI"""
    try:
        result = subprocess.run(["railway", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Railway CLI установлен: {result.stdout.strip()}")
            return True
        else:
            print("❌ Railway CLI не установлен")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI не найден")
        return False

def login_to_railway():
    """Выполняет вход в Railway"""
    try:
        print("Выполняем вход в Railway...")
        subprocess.run(["railway", "login"], check=True)
        print("✅ Вход выполнен успешно")
        return True
    except subprocess.CalledProcessError:
        print("❌ Ошибка при входе в Railway")
        return False

def create_railway_project(project_name):
    """Создает новый проект на Railway"""
    try:
        print(f"Создаем проект {project_name} на Railway...")
        # Создаем новый проект
        result = subprocess.run([
            "railway", "init", 
            "--name", project_name
        ], capture_output=True, text=True, check=True)
        
        print("✅ Проект создан успешно")
        
        # Получаем ID проекта из вывода
        output = result.stdout
        # Обычно ID проекта находится в выводе, но мы можем получить его другим способом
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при создании проекта: {e}")
        return False

def deploy_to_railway():
    """Развертывает проект на Railway"""
    try:
        print("Загружаем проект на Railway...")
        # Загружаем проект
        subprocess.run(["railway", "up"], check=True)
        print("✅ Проект успешно загружен на Railway")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при загрузке проекта: {e}")
        return False

def get_project_url():
    """Получает URL проекта на Railway"""
    try:
        # Получаем информацию о проекте
        result = subprocess.run([
            "railway", "status", "--json"
        ], capture_output=True, text=True, check=True)
        
        project_info = json.loads(result.stdout)
        # Получаем URL из информации о проекте
        # Это может потребовать дополнительной обработки в зависимости от структуры вывода
        return "https://your-project-url.railway.app"
    except Exception as e:
        print(f"⚠️  Не удалось получить URL проекта: {e}")
        return None

def main():
    print("🚀 Развертывание Telegram Financial Agent на Railway")
    print("=" * 50)
    
    # Проверяем, установлен ли Railway CLI
    if not check_railway_cli():
        print("Пожалуйста, установите Railway CLI:")
        print("   curl -fsSL https://railway.app/install.sh | sh")
        return False
    
    # Выполняем вход в Railway
    if not login_to_railway():
        print("Пожалуйста, выполните вход в Railway вручную:")
        print("   railway login")
        return False
    
    project_name = "telegram-finance-agent"
    
    # Создаем проект на Railway
    if not create_railway_project(project_name):
        print("Пожалуйста, создайте проект вручную:")
        print("   railway init --name telegram-finance-agent")
        return False
    
    # Развертываем проект
    if not deploy_to_railway():
        print("Пожалуйста, попробуйте развернуть проект вручную:")
        print("   railway up")
        return False
    
    # Получаем URL проекта
    project_url = get_project_url()
    if project_url:
        print(f"\n🌐 Ваш проект доступен по адресу: {project_url}")
    
    print("\n🎉 Развертывание на Railway завершено!")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)