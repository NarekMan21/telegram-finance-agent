@echo off
title Развертывание Telegram Financial Agent на GitHub
echo ==================================================
echo Telegram Financial Agent - Развертывание на GitHub
echo ==================================================
echo.

echo Проверка Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Ошибка: Python не найден!
    echo Пожалуйста, установите Python 3.7 или выше
    pause
    exit /b 1
)

echo.
echo Запуск скрипта развертывания...
python deploy_to_github.py

if %errorlevel% neq 0 (
    echo.
    echo Ошибка при развертывании
    pause
    exit /b 1
)

echo.
echo Развертывание завершено успешно!
pause