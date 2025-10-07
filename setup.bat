@echo off
title Telegram Financial Agent
echo ==================================================
echo Telegram Financial Agent - Установка и запуск
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

echo Установка зависимостей и запуск приложения...
echo.
python setup_and_run.py

if %errorlevel% neq 0 (
    echo.
    echo Возникли ошибки при установке зависимостей
    pause
    exit /b 1
)

echo.
echo ==================================================
echo Для запуска приложения выполните:
echo python app.py
echo.
echo Или запустите start.bat
echo ==================================================
echo.
pause