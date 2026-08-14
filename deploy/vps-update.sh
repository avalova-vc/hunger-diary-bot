#!/usr/bin/env bash
# Update hunger-bot on VPS: backup DB, migrate .env, install new code.
# Run on VPS as root: bash deploy/vps-update.sh
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/hunger-bot}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Запустите от root: sudo bash deploy/vps-update.sh"
  exit 1
fi

if [[ -f "${APP_DIR}/data/bot.db" ]]; then
  backup="${APP_DIR}/data/bot.db.bak-$(date +%F-%H%M)"
  cp "${APP_DIR}/data/bot.db" "${backup}"
  echo "Backup: ${backup}"
  BEFORE="$(python3.12 -c "import sqlite3; c=sqlite3.connect('${APP_DIR}/data/bot.db'); print(c.execute('select count(*) from events').fetchone()[0])")"
  echo "Events before update: ${BEFORE}"
fi

python3.12 "${REPO_DIR}/deploy/migrate_env.py" "${APP_DIR}/.env"
bash "${REPO_DIR}/deploy/install.sh"

if [[ -f "${APP_DIR}/data/bot.db" ]]; then
  AFTER="$(python3.12 -c "import sqlite3; c=sqlite3.connect('${APP_DIR}/data/bot.db'); print(c.execute('select count(*) from events').fetchone()[0])")"
  echo "Events after update: ${AFTER}"
  SCHEMA="$(python3.12 -c "import sqlite3; c=sqlite3.connect('${APP_DIR}/data/bot.db'); print('user_id' in {r[1] for r in c.execute('pragma table_info(events)').fetchall()})")"
  echo "events.user_id column: ${SCHEMA}"
fi
