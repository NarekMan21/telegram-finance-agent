#!/usr/bin/env python3
"""
Скрипт для проверки доступности GitHub репозитория
"""

import requests
import sys

def check_repo_exists(username, repo_name):
    """Проверяет, существует ли репозиторий на GitHub"""
    url = f"https://api.github.com/repos/{username}/{repo_name}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"✅ Репозиторий https://github.com/{username}/{repo_name} существует")
            repo_data = response.json()
            print(f"   Описание: {repo_data.get('description', 'Нет описания')}")
            print(f"   Звезд: {repo_data.get('stargazers_count', 0)}")
            print(f"   Форков: {repo_data.get('forks_count', 0)}")
            return True
        elif response.status_code == 404:
            print(f"❌ Репозиторий https://github.com/{username}/{repo_name} не найден")
            return False
        else:
            print(f"⚠️  Неожиданный статус ответа: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка при проверке репозитория: {e}")
        return False

def main():
    print("🔍 Проверка доступности GitHub репозитория")
    print("=" * 40)
    
    username = input("Введите ваш GitHub username: ")
    repo_name = input("Введите название репозитория: ")
    
    if check_repo_exists(username, repo_name):
        print("\n✅ Репозиторий доступен для работы")
        return True
    else:
        print("\n❌ Репозиторий недоступен")
        print("Пожалуйста, создайте репозиторий на GitHub:")
        print(f"   1. Перейдите на https://github.com/new")
        print(f"   2. Введите название: {repo_name}")
        print(f"   3. Выберите Public")
        print(f"   4. Не инициализируйте с README")
        print(f"   5. Нажмите 'Create repository'")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)