# Hunger Diary Bot

Telegram-бот — **личный дневник чувства голода и приёмов пищи**.

Не диетолог и не система рекомендаций: бот только помогает быстро фиксировать факты (голод 0–10, приём пищи) и выгружать данные в CSV для анализа в Excel.

> Не заменяет врача или специалиста по РПП.

## Возможности (MVP)

| Функция | Описание |
|---------|----------|
| Голод | Запись уровня 0–10 в любой момент |
| Поела | Тип приёма (завтрак / перекус / обед / ужин) → голод до → сытость после |
| Напоминания | Утром + до 2 напоминаний при тишине 2 часа |
| Экспорт | CSV для Excel |
| Доступ | Один пользователь (whitelist по Telegram ID) |

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
ALLOWED_USER_ID=123456789
WAKE_UP_TIME=07:00
TIMEZONE=Europe/Moscow
SLEEP_TIME=23:00
```

### 3. Запуск

```bash
python -m bot
```

В Telegram откройте бота и отправьте `/start`.

На ПК бот работает **только пока запущен процесс**. Для 24/7 см. [DEPLOY.md](DEPLOY.md).

## Команды в боте

| Действие | Как |
|----------|-----|
| Голод | кнопка **Голод** или `/hunger` |
| Приём пищи | кнопка **Поела** или `/meal` |
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
├── deploy/              # systemd + install.sh для VPS
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
| [DEPLOY.md](DEPLOY.md) | VPS + systemd |

## Безопасность

- Файл `.env` **не коммитьте** (он в `.gitignore`)
- `BOT_TOKEN` — секрет; при утечке отзовите в BotFather
- Бот отвечает только `ALLOWED_USER_ID`

## Стек

Python 3.12 · aiogram 3 · SQLite · APScheduler · systemd (на VPS)

## Лицензия

[MIT](LICENSE)
