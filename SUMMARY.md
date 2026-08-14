# SUMMARY — статус проекта (для агента и разработчика)

> Обновлено: 2026-08-14.  
> Продукт: `CONTEXT.md` · Архитектура: `ARCHITECTURE.md` · UI: `UI_COPY.md` · Деплой: `DEPLOY.md`

## Ссылки

| Что | Где |
|-----|-----|
| GitHub | https://github.com/avalova-vc/hunger-diary-bot |
| Ветка с multi-user | `cursor/multi-user-inactivity` (задеплоена на VPS) |
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
   - голод 0–10; **«Поел(-а)»** (тип → голод до → сытость после);
   - типы: завтрак / перекус / обед / ужин (`snack` без лимита количества);
   - утреннее напоминание + inactivity: до 2 напоминаний, интервал **per-user** в `.env`;
   - экспорт CSV (только свои записи); `/settings` — время пробуждения per-user (в БД);
   - whitelist `ALLOWED_USER_IDS` (до 2); UI на русском.
2. **Мультипользователь (2026-08-14):**
   - `user_id` в `events`, `settings`, `reminder_log`;
   - автомиграция БД v1→v2 при старте (`bot/migrations.py`);
   - на VPS: 29 записей сохранены, все с `user_id=79956169`;
   - второй ID в whitelist пока не добавлен — один пользователь работает штатно.
3. **UI (2026-08-14):** шкала сытости в `/start`, тексты запросов голода/сытости, формат сохранения приёма пищи в две строки.
4. **Деплой:** systemd на VPS; скрипты `deploy/vps-update.sh`, `deploy/migrate_env.py`, `deploy/verify_db.py`.
5. **Документация:** README, DEPLOY, ARCHITECTURE, UI_COPY, CONTEXT.

---

## Решения и почему

| Решение | Почему |
|---------|--------|
| Дневник, не диетолог | Цель — сбор данных для похудения/РПП, без советов |
| Перекус без «1/2» | Не ограничивать число перекусов; различать по времени + типу |
| Inactivity: макс. 2, потом до утра | Мягкие напоминания без спама |
| Inactivity interval в `.env`, не в боте | Персонально, без лишнего UI; пробуждение — через `/settings` |
| SQLite + CSV по запросу | Простой анализ в Excel; данные изолированы по user_id |
| Long polling, не webhook | Проще для MVP, без домена/SSL |
| Python 3.12, не 3.14 | На 3.14 нет готовых wheels (aiohttp/pydantic) |
| Proxy: `.env` `HTTPS_PROXY` или системный | На Windows ПК api.telegram.org через aiohttp падал без прокси; на VPS API доступен напрямую |
| IPv4 preference без прокси | На Windows IPv6 к Telegram часто таймаутился |
| systemd на VPS | Постоянная работа независимо от ПК |
| SSH-ключ `id_ed25519_hungerbot` | Деплой без пароля в чате |
| Тон «Записала», без оценок | Безопасно при работе с перееданием/РПП |

---

## Что осталось / можно дальше

- [x] Мультипользователь (до 2 ID, per-user inactivity в `.env`)
- [x] Деплой multi-user на VPS (2026-08-14)
- [ ] Добавить второй Telegram ID в whitelist (когда будет готов)
- [ ] Слить `cursor/multi-user-inactivity` в `master`
- [ ] Сводки и графики в боте (осознанно отложено)
- [ ] Детализация еды (текст, теги)
- [ ] Контекст: сон, стресс, активность
- [ ] Мультипользователь (>2)
- [ ] Автобэкап CSV/БД в облако
- [ ] При желании: сделать репозиторий public

---

## Подводные камни и договорённости

1. **Один polling на токен.** Не запускать бота одновременно на ПК и на VPS — будет Conflict / «кнопки не работают».
2. **`.env` на диске.** Несохранённый буфер Cursor ≠ файл на диске; токен должен быть реально записан.
3. **Unauthorized** = неверный/отозванный токен; сеть при этом может быть уже ок.
4. **Windows + Telegram:** часто нужен системный прокси (`aiohttp-socks`); на этом VPS — нет.
5. **`deploy/*.sh`:** держать LF (не CRLF), иначе `set: pipefail` на Linux.
6. **Данные** только на машине бота (`data/bot.db`), не в GitHub.
7. **Не выходить за MVP** без явного запроса (см. правило Cursor + `CONTEXT.md`).
8. **Секреты в чат не кидать**; SSH — ключ, пароль только локально.
9. **Миграция БД:** при обновлении — backup `data/bot.db`; старые записи → `user_id` первого ID в whitelist; миграция идемпотентна (schema v2).
10. **Формат `.env`:** `ALLOWED_USER_IDS` + `USER_{id}_WAKE_UP` + `USER_{id}_INACTIVITY_HOURS`. Старый `ALLOWED_USER_ID` поддерживается скриптом `migrate_env.py`.
11. **Добавление второго пользователя:** дописать ID и `USER_{id}_*` в `.env` → `systemctl restart hunger-bot`.
12. Часовой пояс: `Europe/Moscow`, пробуждение по умолчанию `07:00`, inactivity `2` ч, тихие часы с `23:00`.

---

## Быстрые команды

```bash
# статус на VPS
ssh -i ~/.ssh/id_ed25519_hungerbot root@107.189.25.3 \
  "systemctl status hunger-bot; journalctl -u hunger-bot -n 30 --no-pager"

# проверка БД после обновления
ssh -i ~/.ssh/id_ed25519_hungerbot root@107.189.25.3 \
  "python3.12 /opt/hunger-bot/deploy/verify_db.py"

# обновить код на VPS (см. DEPLOY.md — раздел «Обновление»)
# sudo bash deploy/vps-update.sh
```

Windows-ключ: `C:\Users\Amsterdam\.ssh\id_ed25519_hungerbot`.
