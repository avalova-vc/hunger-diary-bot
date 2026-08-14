# SUMMARY — статус проекта (для агента и разработчика)

> Обновлено: 2026-08-14.  
> Продукт: `CONTEXT.md` · Архитектура: `ARCHITECTURE.md` · UI: `UI_COPY.md` · Деплой: `DEPLOY.md`

## Ссылки

| Что | Где |
|-----|-----|
| GitHub | https://github.com/avalova-vc/hunger-diary-bot |
| PR #1 (docs, merged) | https://github.com/avalova-vc/hunger-diary-bot/pull/1 |
| Telegram-бот | `@i_am_hngr_bot` |
| VPS | `107.189.25.3` (IPv6: `2602:fa59:5:868::1`), Ubuntu 24.04 |
| Путь на сервере | `/opt/hunger-bot` |
| systemd | `hunger-bot.service` |
| Владелец GitHub | `avalova-vc` (`avalovaw@gmail.com`) |

Секреты (токен, пароли) — только в локальном `.env` / на сервере `/opt/hunger-bot/.env`, **не в git**.

---

## Что сделано

1. **MVP-бот** (Python 3.12, aiogram 3, SQLite, APScheduler):
   - голод 0–10; «Поела» (тип → голод до → сытость после);
   - типы: завтрак / перекус / обед / ужин (`snack` без лимита количества);
   - утреннее напоминание + inactivity: 1-е через 2 ч, 2-е через 2 ч после 1-го, дальше до утра;
   - экспорт CSV; `/settings` для времени пробуждения;
   - whitelist по `ALLOWED_USER_IDS` (до 2); per-user inactivity в `.env`; UI на русском.
2. **Документация** приведена к читаемому виду (README, DEPLOY без личных IP в инструкции, LICENSE MIT, SECURITY) — влита в `master`.
3. **Деплой на VPS**: бот крутится как systemd-служба 24/7; локальный запуск на ПК остановлен, чтобы не было конфликта polling.
4. **Git**: репозиторий создан, `master` актуален после merge PR #1.

---

## Решения и почему

| Решение | Почему |
|---------|--------|
| Дневник, не диетолог | Цель — сбор данных для похудения/РПП, без советов |
| Перекус без «1/2» | Не ограничивать число перекусов; различать по времени + типу |
| Inactivity: макс. 2, потом до утра | Мягкие напоминания без спама |
| SQLite + CSV по запросу | Простой анализ в Excel; данные изолированы по user_id |
| Long polling, не webhook | Проще для MVP, без домена/SSL |
| Python 3.12, не 3.14 | На 3.14 нет готовых wheels (aiohttp/pydantic) |
| Proxy: `.env` `HTTPS_PROXY` или системный | На Windows ПК api.telegram.org через aiohttp падал без прокси; на VPS API доступен напрямую |
| IPv4 preference без прокси | На Windows IPv6 к Telegram часто таймаутился |
| systemd на VPS | Постоянная работа независимо от ПК |
| SSH-ключ `id_ed25519_hungerbot` | Деплой без пароля в чате |
| Private repo изначально | Личный бот; docs можно открыть публично позже при желании |
| Тон «Записала», без оценок | Безопасно при работе с перееданием/РПП |

---

## Что осталось / можно дальше

- [x] Мультипользователь (до 2 ID, per-user inactivity в `.env`)
- [ ] Сводки и графики в боте (осознанно отложено)
- [ ] Детализация еды (текст, теги)
- [ ] Контекст: сон, стресс, активность
- [ ] Мультипользователь (>2)
- [ ] Автобэкап CSV/БД в облако
- [ ] Синхронизировать код на VPS с последним `master` после doc-only merge (на сервере код бота уже рабочий; docs на VPS не критичны)
- [ ] При желании: сделать репозиторий public

---

## Подводные камни и договорённости

1. **Один polling на токен.** Не запускать бота одновременно на ПК и на VPS — будет Conflict / «кнопки не работают».
2. **`.env` на диске.** Несохранённый буфер Cursor ≠ файл на диске; токен должен быть реально записан.
3. **Unauthorized** = неверный/отозванный токен; сеть при этом может быть уже ок.
4. **Windows + Telegram:** часто нужен системный прокси (`aiohttp-socks`); на этом VPS — нет.
5. **`deploy/install.sh`:** держать LF (не CRLF), иначе `set: pipefail` на Linux.
6. **Данные** только на машине бота (`data/bot.db`), не в GitHub.
7. **Не выходить за MVP** без явного запроса (см. правило Cursor + `CONTEXT.md`).
8. **Секреты в чат не кидать**; SSH — ключ, пароль только локально.
9. Локальный git user для репо: `avalova-vc` / `avalovaw@gmail.com`.
10. **Миграция БД:** при обновлении до multi-user — backup `data/bot.db`; старые записи получают `user_id` первого ID из whitelist.
11. **Формат `.env`:** `ALLOWED_USER_IDS` + `USER_{id}_WAKE_UP` + `USER_{id}_INACTIVITY_HOURS`.
12. Часовой пояс: `Europe/Moscow`, пробуждение по умолчанию `07:00`, тихие часы с `23:00`.

---

## Быстрые команды

```bash
# статус на VPS
ssh -i ~/.ssh/id_ed25519_hungerbot root@107.189.25.3 "systemctl status hunger-bot; journalctl -u hunger-bot -n 30 --no-pager"

# обновить код на VPS (из копии проекта с .env)
# sudo bash deploy/install.sh
```

Windows-ключ обычно: `C:\Users\Amsterdam\.ssh\id_ed25519_hungerbot`.
