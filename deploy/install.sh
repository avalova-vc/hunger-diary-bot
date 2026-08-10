#!/usr/bin/env bash
# Install / update hunger-bot on Ubuntu VPS.
# Run as root: sudo bash deploy/install.sh
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/hunger-bot}"
APP_USER="${APP_USER:-hungerbot}"
SERVICE_NAME="hunger-bot"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Запустите от root: sudo bash deploy/install.sh"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y software-properties-common curl ca-certificates git rsync

# Python 3.12: native on Ubuntu 24.04; on 22.04 use deadsnakes
if ! command -v python3.12 >/dev/null 2>&1; then
  add-apt-repository -y ppa:deadsnakes/ppa
  apt-get update -y
  apt-get install -y python3.12 python3.12-venv python3.12-dev
else
  apt-get install -y python3.12 python3.12-venv python3.12-dev
fi

if ! id -u "${APP_USER}" >/dev/null 2>&1; then
  useradd --system --create-home --home-dir "${APP_DIR}" --shell /usr/sbin/nologin "${APP_USER}"
fi

mkdir -p "${APP_DIR}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

rsync -a \
  --exclude '.venv/' \
  --exclude 'data/' \
  --exclude 'exports/' \
  --exclude '.git/' \
  --exclude '__pycache__/' \
  --exclude '.env' \
  --exclude '*.pyc' \
  "${REPO_DIR}/" "${APP_DIR}/"

mkdir -p "${APP_DIR}/data" "${APP_DIR}/exports"

if [[ ! -f "${APP_DIR}/.env" ]]; then
  if [[ -f "${REPO_DIR}/.env" ]]; then
    cp "${REPO_DIR}/.env" "${APP_DIR}/.env"
    echo "Скопирован .env с машины деплоя."
  else
    cp "${APP_DIR}/.env.example" "${APP_DIR}/.env"
    echo "Создан ${APP_DIR}/.env из примера — ЗАПОЛНИТЕ BOT_TOKEN и ALLOWED_USER_ID."
  fi
fi

python3.12 -m venv "${APP_DIR}/.venv"
"${APP_DIR}/.venv/bin/pip" install --upgrade pip
"${APP_DIR}/.venv/bin/pip" install -r "${APP_DIR}/requirements.txt"

chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}"
chmod 600 "${APP_DIR}/.env"

cp "${APP_DIR}/deploy/hunger-bot.service" "/etc/systemd/system/${SERVICE_NAME}.service"
systemctl daemon-reload
systemctl enable "${SERVICE_NAME}"
systemctl restart "${SERVICE_NAME}"

sleep 2
echo
echo "Статус:"
systemctl --no-pager --full status "${SERVICE_NAME}" || true
echo
echo "Логи: journalctl -u ${SERVICE_NAME} -f"
echo "Проверка Telegram API: curl -I https://api.telegram.org"
