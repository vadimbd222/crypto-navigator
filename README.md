# Крипто-навигатор

Telegram-бот для тех, кто только знакомиться с криптовалютами: показывает курсы монет, конвертирует валюты, присылает свежие новости и объясняет базовые термины на обучающих карточках. Прогресс геймифицирован: за активность начисляются XP, растут уровень и звание, есть таблица лидеров. Бот понимает 8 команд (/start, /price, /convert, /news, /learn, /top, /settings, /help) и дублирует их кнопками на экране.

## Технологии и API

- Python 3.12 — язык разработки
- aiogram 3 — асинхронный фреймворк Telegram Bot API (роутеры, FSM, клавиатуры)
- SQLite + aiosqlite — база данных с асинхронным доступом
- python-dotenv — конфигурация через файл .env
- CoinGecko API — курсы монет и конвертация (кэш с TTL 60 секунд)
- CryptoCompare API — свежие новости о криптовалютах

## Инструкция по развертыванию

### Шаг 1. Получение ключей API

1. Токен бота: в Telegram откройте @BotFather, отправь /newbot, придумайте имя и username — BotFather выдаст строку вида 123456:AA... Это BOT_TOKEN.
2. Ключ новостей: зарегистрируйтесь на cryptocompare.com, откройте раздел API Keys и создайте бесплатный ключ. Это CRYPTOCOMPARE_API_KEY.

### Шаг 2. Установка проекта

    git clone https://github.com/<твой-ник>/crypto-navigator.git
    cd crypto-navigator

    python -m venv venv
    venv\Scripts\activate        # Windows
    source venv/bin/activate     # Linux

    pip install -r requirements.txt

### Шаг 3. Настройка базы данных

Устанавливать и настраивать БД не нужно. При первом запуске bot.py вызывает init_db(), и в папке проекта автоматически создаётся файл bot.db (SQLite, две таблицы — схема ниже). Все данные хранятся в этом одном файле.

### Шаг 4. Запуск

1. Скопируйте .env.example в файл .env и заполни:

       BOT_TOKEN=твой_токен_от_BotFather
       CRYPTOCOMPARE_API_KEY=твой_ключ
       PROXY_URL=

   PROXY_URL нужен только для локального запуска из сетей, где Telegram заблокирован; на сервере его оставляют пустым.

2. Запустите бота:

       python bot.py

3. Откройте бота в Telegram и отправь /start.

## Схема базы данных

Файл bot.db (SQLite), две таблицы.

Таблица users — пользователи и их прогресс:

    telegram_id    INTEGER  PRIMARY KEY   ID пользователя в Telegram
    username       TEXT                   ник в Telegram (может быть пустым)
    xp             INTEGER  DEFAULT 0     накопленный опыт
    level          INTEGER  DEFAULT 1     уровень: xp // 100 + 1
    notifications  INTEGER  DEFAULT 1     уведомления: 1 вкл / 0 выкл

Таблица progress — история активности:

    id         INTEGER  PRIMARY KEY AUTOINCREMENT   номер записи
    user_id    INTEGER                              ссылка на users.telegram_id
    game_type  TEXT                                 тип активности: convert, learn_card...
    score      INTEGER                              результат
    played_at  TEXT                                 дата и время (ISO 8601)

Связь таблиц: users.telegram_id 1 ——— ∞ progress.user_id — у одного пользователя может быть много записей активности.
