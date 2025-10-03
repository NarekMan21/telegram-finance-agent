#!/usr/bin/env python3
"""
Скрипт для развертывания проекта на GitHub
"""

import os
import subprocess
import sys

def main():
    print("🚀 Развертывание Telegram Financial Agent на GitHub")
    print("=" * 50)
    
    # Получаем информацию от пользователя
    username = input("Введите ваш GitHub username: ")
    repo_name = input("Введите название репозитория (например, telegram-financial-agent): ")
    
    # Создаем репозиторий через GitHub CLI (если установлен)
    try:
        # Проверяем, установлен ли GitHub CLI
        subprocess.run(["gh", "--version"], check=True, capture_output=True)
        
        # Создаем репозиторий
        print(f"Создание репозитория {repo_name}...")
        subprocess.run([
            "gh", "repo", "create", repo_name, 
            "--public", 
            "--description", "Telegram Financial Agent - Приложение для отслеживания финансовых операций из Telegram",
            "--homepage", "https://github.com/{}/{}".format(username, repo_name)
        ], check=True)
        
        print("✅ Репозиторий успешно создан!")
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ℹ️  GitHub CLI не найден или не установлен")
        print("📝 Пожалуйста, создайте репозиторий вручную на GitHub:")
        print(f"   1. Перейдите на https://github.com/new")
        print(f"   2. Введите название: {repo_name}")
        print(f"   3. Выберите Public")
        print(f"   4. Не инициализируйте с README")
        print(f"   5. Нажмите 'Create repository'")
        input("Нажмите Enter после создания репозитория...")
    
    # Добавляем remote и пушим код
    try:
        print("Настройка Git remote...")
        # Проверяем, существует ли уже remote origin
        result = subprocess.run(["git", "remote"], capture_output=True, text=True)
        remotes = result.stdout.strip().split('\n')
        
        if 'origin' in remotes:
            # Если remote origin уже существует, обновляем его
            subprocess.run([
                "git", "remote", "set-url", "origin", 
                f"https://github.com/{username}/{repo_name}.git"
            ], check=True)
            print("Обновлен существующий remote origin")
        else:
            # Если remote origin не существует, создаем его
            subprocess.run([
                "git", "remote", "add", "origin", 
                f"https://github.com/{username}/{repo_name}.git"
            ], check=True)
            print("Создан новый remote origin")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при настройке Git remote: {e}")
        return False
    
    print("Загрузка кода на GitHub...")
    try:
        # Пушим код
        subprocess.run(["git", "push", "-u", "origin", "master"], check=True)
        print("✅ Код успешно загружен на GitHub!")
    except subprocess.CalledProcessError:
        print("❌ Ошибка при загрузке кода")
        print("Попробуйте выполнить вручную:")
        print(f"   git push -u origin master")
        return False
    
    print("\n🎉 Развертывание завершено!")
    print(f"🔗 Ваш репозиторий: https://github.com/{username}/{repo_name}")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)