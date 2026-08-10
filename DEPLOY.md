# Деплой на VPS (Ubuntu)

Бот работает 24/7 как systemd-служба в `/opt/hunger-bot`.

## Важно про ваши адреса

| Адрес | Тип | Заметка |
|-------|-----|---------|
| `107.189.25.3` | публичный IPv4 | Основной адрес для SSH |
| `2602:fa59:5:868::1` | публичный IPv6 | Запасной, если IPv4 недоступен |

---

## Безопасный доступ (пароли не в чат)

1. На ПК запустите: `deploy\make-ssh-key.ps1` — создаст ключ `~\.ssh\id_ed25519_hungerbot`.
2. **Публичный** ключ (файл `.pub` или вывод скрипта) добавьте на VPS:
   - в панели хостинга → SSH Keys, **или**
   - один раз у себя в терминале по паролю (пароль вводите только локально):

```powershell
type $env:USERPROFILE\.ssh\id_ed25519_hungerbot.pub | ssh root@107.189.25.3 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

3. Приватный ключ и пароль **никогда не присылайте в чат**.
4. Локальные настройки хоста: `deploy/secrets.env` (в `.gitignore`).

Когда ключ добавлен, напишите: «ключ добавлен, можно деплоить».

---

## Вариант A — я ставлю по SSH (после доступа по ключу)

1. Проверить `curl -I https://api.telegram.org`
2. Скопировать проект + `.env`
3. Запустить `deploy/install.sh`
4. Проверить `systemctl status hunger-bot` и ответ бота на `/start`

Если Telegram с VPS недоступен — добавим в `.env` строку `HTTPS_PROXY=...`.

---

## Вариант B — сами на сервере

### 1. Подключиться

```bash
ssh USER@VPS_IP
```

### 2. Загрузить проект

С вашего ПК (PowerShell), из папки проекта:

```powershell
scp -r . USER@VPS_IP:~/hunger-bot
```

### 3. Установить

На VPS:

```bash
cd ~/hunger-bot
sudo bash deploy/install.sh
```

### 4. Проверить `.env` и логи

```bash
sudo nano /opt/hunger-bot/.env
sudo systemctl restart hunger-bot
sudo systemctl status hunger-bot
sudo journalctl -u hunger-bot -f
```

Опционально при блокировке Telegram:
```env
HTTPS_PROXY=http://127.0.0.1:1080
```

---

## Полезные команды

| Действие | Команда |
|----------|---------|
| Перезапуск | `sudo systemctl restart hunger-bot` |
| Логи | `sudo journalctl -u hunger-bot -n 100` |
| Обновить код | снова `sudo bash deploy/install.sh` |

Данные (SQLite): `/opt/hunger-bot/data/` — при обновлении не удаляются.
