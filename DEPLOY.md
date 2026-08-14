# Деплой на VPS (Ubuntu 22.04 / 24.04)

Бот как systemd-служба в `/opt/hunger-bot`: автозапуск после перезагрузки и рестарт при падении.

## Требования

- VPS с Ubuntu и доступом по SSH
- Python 3.12 (скрипт установки поставит сам)
- Заполненный `.env` (токен и Telegram ID в whitelist)
- С сервера должен открываться `https://api.telegram.org`  
  (если нет — укажите `HTTPS_PROXY` в `.env`)

## Формат `.env`

```env
BOT_TOKEN=...
ALLOWED_USER_IDS=123456789
USER_123456789_WAKE_UP=07:00
USER_123456789_INACTIVITY_HOURS=2
TIMEZONE=Europe/Moscow
SLEEP_TIME=23:00
```

Для **двух пользователей**:

```env
ALLOWED_USER_IDS=123456789,987654321
USER_123456789_WAKE_UP=07:00
USER_123456789_INACTIVITY_HOURS=2
USER_987654321_WAKE_UP=08:00
USER_987654321_INACTIVITY_HOURS=3
```

| Переменная | Где задаётся | Описание |
|------------|--------------|----------|
| `ALLOWED_USER_IDS` | `.env` | Whitelist (1–2 ID через запятую) |
| `USER_{id}_WAKE_UP` | `.env` | Дефолт пробуждения; дальше меняется через `/settings` |
| `USER_{id}_INACTIVITY_HOURS` | `.env` | Интервал между inactivity-напоминаниями (часы, можно дробное) |
| `TIMEZONE`, `SLEEP_TIME` | `.env` | Общие для всех пользователей |

Старый формат (`ALLOWED_USER_ID`, `WAKE_UP_TIME`) автоматически конвертируется скриптом `deploy/migrate_env.py`.

---

## Безопасный SSH (рекомендуется)

1. Создайте ключ на своём ПК:

```powershell
# Windows
.\deploy\make-ssh-key.ps1
```

```bash
# Linux / macOS
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_hungerbot -C "hungerbot-deploy"
```

2. Добавьте **публичный** ключ (`.pub`) на сервер — в панели хостинга или так:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519_hungerbot.pub USER@VPS_IP
```

Windows (PowerShell), пароль вводите только локально:

```powershell
type $env:USERPROFILE\.ssh\id_ed25519_hungerbot.pub | ssh USER@VPS_IP "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

3. Приватный ключ и пароли **не публикуйте** и не коммитьте.  
   Локально можно хранить хост в `deploy/secrets.env` (файл в `.gitignore`, см. `deploy/secrets.example.env`).

---

## Первая установка

### 1. Скопируйте проект на сервер

```bash
# с вашего компьютера
scp -r . USER@VPS_IP:~/hunger-diary-bot
```

Или клонируйте репозиторий на VPS:

```bash
git clone -b cursor/multi-user-inactivity https://github.com/avalova-vc/hunger-diary-bot.git ~/hunger-diary-bot
```

### 2. Положите `.env`

На сервере в `/opt/hunger-bot/.env` (скопируйте с ПК или создайте из `.env.example`).

### 3. Запустите установщик

```bash
cd ~/hunger-diary-bot
sudo bash deploy/install.sh
```

Скрипт:

- ставит Python 3.12 и зависимости
- создаёт системного пользователя `hungerbot`
- копирует код в `/opt/hunger-bot` (каталог `data/` **не затирается**)
- включает и перезапускает службу `hunger-bot`

### 4. Проверьте

```bash
sudo systemctl status hunger-bot
sudo journalctl -u hunger-bot -n 50 --no-pager
python3.12 /opt/hunger-bot/deploy/verify_db.py
```

В Telegram: `/start` — кнопка **Поел(-а)**, `/export` — ваши записи.

---

## Обновление (рекомендуется)

Скрипт `deploy/vps-update.sh` делает всё за один проход:

1. Backup `data/bot.db` → `data/bot.db.bak-YYYY-MM-DD-HHMM`
2. Миграция `.env` (если ещё старый формат)
3. `deploy/install.sh` — код + перезапуск
4. Проверка числа записей до/после

### С ПК (Windows PowerShell)

```powershell
$proj = "C:\path\to\hunger-diary-bot"
$tar = "$env:TEMP\hunger-bot-deploy.tar"
tar -cf $tar --exclude=.venv --exclude=data --exclude=.git --exclude=exports --exclude=__pycache__ --exclude=.env -C $proj .
scp -i $env:USERPROFILE\.ssh\id_ed25519_hungerbot $tar root@VPS_IP:/tmp/hunger-bot-deploy.tar
ssh -i $env:USERPROFILE\.ssh\id_ed25519_hungerbot root@VPS_IP `
  "rm -rf /root/hunger-diary-bot && mkdir -p /root/hunger-diary-bot && tar xf /tmp/hunger-bot-deploy.tar -C /root/hunger-diary-bot && sed -i 's/\r$//' /root/hunger-diary-bot/deploy/*.sh && bash /root/hunger-diary-bot/deploy/vps-update.sh"
```

### На VPS (если репо уже клонировано)

```bash
cd ~/hunger-diary-bot
git pull
sudo bash deploy/vps-update.sh
```

### Миграция БД

При первом запуске новой версии бот автоматически:

- добавляет `user_id` в `events` и `reminder_log`
- переводит `settings` на PK = `user_id`
- присваивает существующим записям `user_id` первого ID из whitelist

В логах: `Migrating database to schema v2` → `Migration complete`.

Проверка:

```bash
python3.12 /opt/hunger-bot/deploy/verify_db.py
# events cols: [..., 'user_id']
# schema version: 2
```

---

## Добавить второго пользователя

1. Узнайте Telegram user ID второго человека ([@userinfobot](https://t.me/userinfobot)).
2. Отредактируйте `/opt/hunger-bot/.env`:

```env
ALLOWED_USER_IDS=79956169,НОВЫЙ_ID
USER_79956169_WAKE_UP=07:00
USER_79956169_INACTIVITY_HOURS=2
USER_НОВЫЙ_ID_WAKE_UP=08:00
USER_НОВЫЙ_ID_INACTIVITY_HOURS=2
```

3. Перезапуск:

```bash
sudo systemctl restart hunger-bot
```

Новый пользователь начнёт с пустой историей; данные первого не затрагиваются.

---

## Полезные команды

| Действие | Команда |
|----------|---------|
| Статус | `sudo systemctl status hunger-bot` |
| Перезапуск | `sudo systemctl restart hunger-bot` |
| Логи | `sudo journalctl -u hunger-bot -f` |
| Обновить код | `sudo bash deploy/vps-update.sh` |
| Проверить БД | `python3.12 /opt/hunger-bot/deploy/verify_db.py` |
| Backup БД вручную | `cp /opt/hunger-bot/data/bot.db /opt/hunger-bot/data/bot.db.bak-$(date +%F)` |

База SQLite: `/opt/hunger-bot/data/bot.db`.

---

## Прокси до Telegram

Если с VPS нет доступа к API:

```env
HTTPS_PROXY=http://127.0.0.1:1080
```

Затем: `sudo systemctl restart hunger-bot`.

---

## Скрипты в `deploy/`

| Файл | Назначение |
|------|------------|
| `install.sh` | Первая установка / синхронизация кода в `/opt/hunger-bot` |
| `vps-update.sh` | Обновление: backup + migrate env + install |
| `migrate_env.py` | Конвертация `.env` single-user → multi-user |
| `verify_db.py` | Проверка schema v2 и числа записей |
| `hunger-bot.service` | Unit systemd |

---

## История

| Дата | Событие |
|------|---------|
| 2026-08-10 | Первый деплой MVP на VPS |
| 2026-08-14 | Multi-user, per-user inactivity, UI; деплой через `vps-update.sh`; 29 записей мигрированы без потерь |
