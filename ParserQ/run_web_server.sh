#!/bin/bash

echo "Telegram Финансовый Веб-Сервер"
echo "=============================="
echo

# Проверка установлен ли Python
if ! command -v python3 &> /dev/null
then
    echo "Ошибка: Python 3 не установлен"
    echo "Пожалуйста, установите Python 3.7 или новее и попробуйте снова"
    exit 1
fi

echo "Запуск Telegram Финансового Веб-Сервера..."
echo "Откройте браузер и перейдите по адресу http://localhost:5000"
echo
python3 run_full_system.py