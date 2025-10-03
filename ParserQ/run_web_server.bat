@echo off
echo Telegram Финансовый Веб-Сервер
echo ==============================
echo.

REM Проверка установлен ли Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Ошибка: Python не установлен или не находится в PATH
    echo Пожалуйста, установите Python 3.7 или новее и попробуйте снова
    pause
    exit /b 1
)

echo Запуск Telegram Финансового Веб-Сервера...
echo Откройте браузер и перейдите по адресу http://localhost:5000
echo.
python run_full_system.py

pause