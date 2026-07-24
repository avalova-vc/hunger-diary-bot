# Дневник голода и питания — Telegram-бот (MVP)

Личный бот для записи чувства голода (0–10) и приёмов пищи. Данные сохраняются в SQLite и выгружаются в CSV.

Подробности: `CONTEXT.md`, `ARCHITECTURE.md`, `UI_COPY.md`.

## Требования

- **Python 3.12** (рекомендуется; системный 3.14 пока плохо поддерживается пакетами бота)
- Telegram Bot Token и ваш User ID в `.env`
- Git (для версионирования)

## Установка

```powershell
cd "C:\Users\Amsterdam\Desktop\cursor folder\бот чувства голода"
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Скопируйте `.env.example` в `.env` (если ещё нет) и заполните:

```env
BOT_TOKEN=...
ALLOWED_USER_ID=...
WAKE_UP_TIME=07:00
TIMEZONE=Europe/Moscow
SLEEP_TIME=23:00
```

## Запуск

```powershell
python -m bot
```

В Telegram напишите боту `/start`.

**Важно:** напоминания работают только пока запущен этот процесс (ПК включён).

## Команды

| Действие | Как |
|----------|-----|
| Голод | кнопка «Голод» или `/hunger` |
| Приём пищи | кнопка «Поела» или `/meal` |
| Экспорт CSV | кнопка «Экспорт» или `/export` |
| Время пробуждения | `/settings` |

## Git

`.env`, `data/`, `exports/` и виртуальное окружение **не** коммитятся (см. `.gitignore`).
