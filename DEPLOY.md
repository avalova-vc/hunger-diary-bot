# Деплой на VPS (Ubuntu 22.04 / 24.04)

Бот как systemd-служба в `/opt/hunger-bot`: автозапуск после перезагрузки и рестарт при падении.

## Требования

- VPS с Ubuntu и доступом по SSH
- Python 3.12 (скрипт установки поставит сам)
- Заполненный `.env` (токен и ваш Telegram ID)
- С сервера должен открываться `https://api.telegram.org`  
  (если нет — укажите `HTTPS_PROXY` в `.env`)

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

## Установка

### 1. Скопируйте проект на сервер

```bash
# с вашего компьютера
scp -r . USER@VPS_IP:~/hunger-diary-bot
```

Или клонируйте репозиторий прямо на VPS (если он доступен серверу).

### 2. Положите `.env`

На сервере в корне проекта должен быть `.env` (скопируйте с ПК или создайте из `.env.example`).

### 3. Запустите установщик

```bash
cd ~/hunger-diary-bot
sudo bash deploy/install.sh
```

Скрипт:

- ставит Python 3.12 и зависимости
- создаёт системного пользователя `hungerbot`
- копирует код в `/opt/hunger-bot` (каталог `data/` не затирается)
- включает службу `hunger-bot`

### 4. Проверьте

```bash
sudo systemctl status hunger-bot
sudo journalctl -u hunger-bot -n 50 --no-pager
```

В Telegram: `/start`.

## Полезные команды

| Действие | Команда |
|----------|---------|
| Статус | `sudo systemctl status hunger-bot` |
| Перезапуск | `sudo systemctl restart hunger-bot` |
| Логи | `sudo journalctl -u hunger-bot -f` |
| Обновить код | снова `sudo bash deploy/install.sh` из новой копии проекта |

База SQLite: `/opt/hunger-bot/data/bot.db`.

## Прокси до Telegram

Если с VPS нет доступа к API:

```env
HTTPS_PROXY=http://127.0.0.1:1080
```

Затем: `sudo systemctl restart hunger-bot`.
