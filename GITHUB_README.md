# Telegram Финансовый Агент

Telegram Финансовый Агент - это веб-приложение для отслеживания финансовых операций из Telegram групп. Приложение предоставляет удобный мобильный интерфейс для анализа доходов и расходов.

## Особенности

- 📱 Мобильный-first дизайн
- 📊 Интерактивные графики и аналитика
- 🔐 Безопасное подключение к Telegram API
- 📈 Финансовая аналитика и инсайты
- 🔔 Уведомления о новых операциях
- 💾 Экспорт/импорт данных

## Установка и запуск

### 1. Получение Telegram API ключей

Перед запуском необходимо получить API ключи:

1. Перейдите на https://my.telegram.org
2. Войдите с вашим номером телефона
3. Выберите "API Development Tools"
4. Создайте новое приложение
5. Сохраните полученные `api_id` и `api_hash`

### 2. Настройка конфигурации

Отредактируйте `config.json`:

```json
{
    "api_id": ВАШ_API_ID,
    "api_hash": "ВАШ_API_HASH",
    "phone_number": "+79281234567",
    "group_ids": [-1001234567890, -1000987654321],
    "group_types": {
        "-1001234567890": "income",
        "-1000987654321": "expense"
    }
}
```

### 3. Запуск приложения

#### Вариант A: Flask приложение (рекомендуется)
```bash
# Установите зависимости
pip install -r requirements.txt

# Запустите Flask приложение
python app.py 8080

# В отдельном терминале запустите Telegram парсер
python run_parser.py
```

#### Вариант B: Только веб-интерфейс
```bash
# Запустите статический сервер
python server.py 8080
```

## Развертывание как Telegram Mini App

Для развертывания приложения как Telegram Mini App следуйте инструкциям в файле [TELEGRAM_MINI_APP_DEPLOY.md](TELEGRAM_MINI_APP_DEPLOY.md).

## Развертывание в облаке

#### Heroku
```bash
# Установите Heroku CLI
heroku login

# Создайте приложение
heroku create your-app-name

# Загрузите код
git push heroku main
```

#### Railway
```bash
# Установите Railway CLI
railway login

# Инициализируйте проект
railway init

# Разверните
railway up
```

#### Vercel
```bash
# Установите Vercel CLI
npm i -g vercel

# Разверните
vercel --prod
```

## Лицензия

MIT License