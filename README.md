# Hunger Diary Bot

Telegram-бот — **личный дневник чувства голода и приёмов пищи**.

Не диетолог и не система рекомендаций: бот только помогает быстро фиксировать факты (голод 0–10, приём пищи) и выгружать данные в CSV для анализа в Excel.

> Не заменяет врача или специалиста по РПП.

## Возможности (MVP)

| Функция | Описание |
|---------|----------|
| Голод | Запись уровня 0–10 в любой момент |
| Поел(-а) | Тип → голод до → сытость после → время (Сейчас / −15/−30/−60 мин / ЧЧ:ММ) |
| Напоминания | Утром + до 2 inactivity (интервал per-user в `.env`) |
| Экспорт | CSV для Excel |
| Доступ | До 2 пользователей (whitelist по Telegram ID) |

Интерфейс на **русском**. Перекусов за день — сколько угодно.

## Быстрый старт

### 1. Что нужно

- Python **3.12**
- Токен бота от [@BotFather](https://t.me/BotFather)
- Ваш Telegram user ID (например, [@userinfobot](https://t.me/userinfobot))

### 2. Установка

```bash
git clone https://github.com/avalova-vc/hunger-diary-bot.git
cd hunger-diary-bot

python3.12 -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
# .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
cp .env.example .env
```

Заполните `.env`:

```env
BOT_TOKEN=123456:ABC...
ALLOWED_USER_IDS=123456789
USER_123456789_WAKE_UP=07:00
USER_123456789_INACTIVITY_HOURS=2
TIMEZONE=Europe/Moscow
SLEEP_TIME=23:00
```

### 3. Запуск

```bash
python -m bot
```

В Telegram откройте бота и отправьте `/start`.

На ПК бот работает **только пока запущен процесс**. Для 24/7 см. [DEPLOY.md](DEPLOY.md).

## Обновление на VPS

Кратко:

```bash
cd ~/hunger-diary-bot && git pull
sudo bash deploy/vps-update.sh
python3.12 /opt/hunger-bot/deploy/verify_db.py
```

Подробности, формат `.env`, добавление второго пользователя и миграция БД — в [DEPLOY.md](DEPLOY.md).

## Команды в боте

| Действие | Как |
|----------|-----|
| Голод | кнопка **Голод** или `/hunger` |
| Приём пищи | кнопка **Поел(-а)** или `/meal` |
| Экспорт CSV | кнопка **Экспорт** или `/export` |
| Время пробуждения | `/settings` |

## Структура проекта

```
hunger-diary-bot/
├── bot/                 # код бота (aiogram 3)
│   ├── handlers/        # команды и сценарии
│   ├── services/        # CSV, логика напоминаний
│   ├── models/          # SQLAlchemy / SQLite
│   └── ...
├── deploy/              # install.sh, vps-update.sh, migrate_env.py, verify_db.py
├── CONTEXT.md           # продукт и границы MVP
├── ARCHITECTURE.md      # техническая архитектура
├── UI_COPY.md           # тексты кнопок и сообщений
├── DEPLOY.md            # установка на сервер
├── .env.example         # шаблон настроек
└── requirements.txt
```

## Документация

| Файл | Зачем читать |
|------|----------------|
| [CONTEXT.md](CONTEXT.md) | Идея, MVP, что сознательно не делаем |
| [SUMMARY.md](SUMMARY.md) | Статус, решения, ссылки, подводные камни |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Стек, БД, напоминания, деплой |
| [UI_COPY.md](UI_COPY.md) | Все тексты интерфейса |
| [DEPLOY.md](DEPLOY.md) | VPS + systemd + **обновление и миграция** |

## Безопасность

- Файл `.env` **не коммитьте** (он в `.gitignore`)
- `BOT_TOKEN` — секрет; при утечке отзовите в BotFather
- Бот отвечает только ID из `ALLOWED_USER_IDS` (до 2)

## Стек

Python 3.12 · aiogram 3 · SQLite · APScheduler · systemd (на VPS)

## Лицензия

[MIT](LICENSE)
