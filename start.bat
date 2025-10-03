@echo off
title Telegram Financial Agent - Режим реального времени
echo ==================================================
echo Telegram Financial Agent - Запуск в режиме реального времени
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
echo Проверка конфигурационного файла...
if not exist "config.json" (
    echo Ошибка: Файл config.json не найден!
    echo Пожалуйста, создайте config.json с настройками Telegram API
    pause
    exit /b 1
)

echo.
echo Проверка необходимых файлов...
set missing_files=0
if not exist "app.py" (
    echo Ошибка: Файл app.py не найден!
    set missing_files=1
)
if not exist "run_parser.py" (
    echo Ошибка: Файл run_parser.py не найден!
    set missing_files=1
)
if not exist "index.html" (
    echo Ошибка: Файл index.html не найден!
    set missing_files=1
)
if not exist "main.js" (
    echo Ошибка: Файл main.js не найден!
    set missing_files=1
)

if %missing_files% equ 1 (
    echo Пожалуйста, убедитесь, что все необходимые файлы присутствуют
    pause
    exit /b 1
)

echo Все необходимые файлы найдены
echo.
echo Запуск Telegram Financial Agent в режиме реального времени...
echo.
echo Веб-интерфейс будет доступен по адресу: http://localhost:8080
echo Для остановки всех компонентов нажмите Ctrl+C
echo.
python start_full.py
if %errorlevel% neq 0 (
    echo.
    echo Ошибка при запуске Telegram Financial Agent
    pause
    exit /b 1
)
pause