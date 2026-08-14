from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

DEFAULT_INACTIVITY_HOURS = 2.0
MAX_ALLOWED_USERS = 2


@dataclass(frozen=True)
class UserConfig:
    user_id: int
    wake_up_time: str
    inactivity_hours: float


@dataclass(frozen=True)
class Config:
    bot_token: str
    allowed_user_ids: tuple[int, ...]
    users: dict[int, UserConfig]
    timezone: str
    sleep_time: str
    db_path: Path
    exports_dir: Path

    @property
    def legacy_user_id(self) -> int:
        return self.allowed_user_ids[0]


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value or value.startswith("YOUR_"):
        raise RuntimeError(f"Заполните {name} в файле .env")
    return value


def _parse_allowed_user_ids() -> list[int]:
    raw = os.getenv("ALLOWED_USER_IDS", "").strip()
    if raw:
        ids = [int(part.strip()) for part in raw.split(",") if part.strip()]
    else:
        legacy = os.getenv("ALLOWED_USER_ID", "").strip()
        if not legacy or legacy.startswith("YOUR_"):
            raise RuntimeError("Заполните ALLOWED_USER_IDS (или ALLOWED_USER_ID) в файле .env")
        ids = [int(legacy)]

    if not ids:
        raise RuntimeError("ALLOWED_USER_IDS не должен быть пустым")
    if len(ids) > MAX_ALLOWED_USERS:
        raise RuntimeError(f"Максимум {MAX_ALLOWED_USERS} пользователя в ALLOWED_USER_IDS")
    return ids


def _parse_user_configs(user_ids: list[int]) -> dict[int, UserConfig]:
    default_wake = os.getenv("WAKE_UP_TIME", "08:00").strip()
    default_inactivity = os.getenv("INACTIVITY_HOURS", str(DEFAULT_INACTIVITY_HOURS)).strip()

    users: dict[int, UserConfig] = {}
    for user_id in user_ids:
        wake = os.getenv(f"USER_{user_id}_WAKE_UP", default_wake).strip()
        inactivity_raw = os.getenv(f"USER_{user_id}_INACTIVITY_HOURS", default_inactivity).strip()
        try:
            inactivity_hours = float(inactivity_raw)
        except ValueError as exc:
            raise RuntimeError(
                f"USER_{user_id}_INACTIVITY_HOURS должно быть числом, получено: {inactivity_raw!r}"
            ) from exc
        if inactivity_hours <= 0:
            raise RuntimeError(f"USER_{user_id}_INACTIVITY_HOURS должно быть > 0")
        users[user_id] = UserConfig(user_id, wake, inactivity_hours)
    return users


def load_config() -> Config:
    data_dir = ROOT_DIR / "data"
    exports_dir = ROOT_DIR / "exports"
    data_dir.mkdir(exist_ok=True)
    exports_dir.mkdir(exist_ok=True)

    allowed_user_ids = tuple(_parse_allowed_user_ids())

    return Config(
        bot_token=_require("BOT_TOKEN"),
        allowed_user_ids=allowed_user_ids,
        users=_parse_user_configs(list(allowed_user_ids)),
        timezone=os.getenv("TIMEZONE", "Europe/Moscow").strip(),
        sleep_time=os.getenv("SLEEP_TIME", "23:00").strip(),
        db_path=data_dir / "bot.db",
        exports_dir=exports_dir,
    )
