from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Config:
    bot_token: str
    allowed_user_id: int
    wake_up_time: str
    timezone: str
    sleep_time: str
    db_path: Path
    exports_dir: Path


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value or value.startswith("YOUR_"):
        raise RuntimeError(f"Заполните {name} в файле .env")
    return value


def load_config() -> Config:
    data_dir = ROOT_DIR / "data"
    exports_dir = ROOT_DIR / "exports"
    data_dir.mkdir(exist_ok=True)
    exports_dir.mkdir(exist_ok=True)

    return Config(
        bot_token=_require("BOT_TOKEN"),
        allowed_user_id=int(_require("ALLOWED_USER_ID")),
        wake_up_time=os.getenv("WAKE_UP_TIME", "08:00").strip(),
        timezone=os.getenv("TIMEZONE", "Europe/Moscow").strip(),
        sleep_time=os.getenv("SLEEP_TIME", "23:00").strip(),
        db_path=data_dir / "bot.db",
        exports_dir=exports_dir,
    )
