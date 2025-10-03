@echo off
title Развертывание Telegram Financial Agent на Railway
echo ==================================================
echo Telegram Financial Agent - Развертывание на Railway
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
echo Запуск скрипта развертывания на Railway...
python deploy_to_railway.py

if %errorlevel% neq 0 (
    echo.
    echo Ошибка при развертывании на Railway
    pause
    exit /b 1
)

echo.
echo Развертывание на Railway завершено успешно!
pause