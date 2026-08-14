from __future__ import annotations

import logging
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 2


def _table_exists(engine: Engine, name: str) -> bool:
    return name in inspect(engine).get_table_names()


def _column_exists(engine: Engine, table: str, column: str) -> bool:
    if not _table_exists(engine, table):
        return False
    return column in {col["name"] for col in inspect(engine).get_columns(table)}


def _current_version(engine: Engine) -> int:
    if not _table_exists(engine, "schema_meta"):
        return 0
    with engine.connect() as conn:
        row = conn.execute(text("SELECT version FROM schema_meta LIMIT 1")).first()
    return int(row[0]) if row else 0


def _set_version(engine: Engine, version: int) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS schema_meta ("
                "id INTEGER PRIMARY KEY CHECK (id = 1), "
                "version INTEGER NOT NULL)"
            )
        )
        conn.execute(text("DELETE FROM schema_meta"))
        conn.execute(text("INSERT INTO schema_meta (id, version) VALUES (1, :v)"), {"v": version})


def run_migrations(engine: Engine, legacy_user_id: int, all_user_ids: list[int]) -> None:
    version = _current_version(engine)
    if version >= SCHEMA_VERSION:
        return

    if not _table_exists(engine, "events"):
        logger.info("Fresh database — schema v%s will be created", SCHEMA_VERSION)
        _set_version(engine, SCHEMA_VERSION)
        return

    logger.info("Migrating database to schema v%s (legacy user_id=%s)", SCHEMA_VERSION, legacy_user_id)

    with engine.begin() as conn:
        if not _column_exists(engine, "events", "user_id"):
            conn.execute(text("ALTER TABLE events ADD COLUMN user_id INTEGER"))
            conn.execute(
                text("UPDATE events SET user_id = :uid WHERE user_id IS NULL"),
                {"uid": legacy_user_id},
            )

        if not _column_exists(engine, "reminder_log", "user_id"):
            conn.execute(text("ALTER TABLE reminder_log ADD COLUMN user_id INTEGER"))
            conn.execute(
                text("UPDATE reminder_log SET user_id = :uid WHERE user_id IS NULL"),
                {"uid": legacy_user_id},
            )

        settings_cols = {col["name"] for col in inspect(engine).get_columns("settings")}
        if "id" in settings_cols and "user_id" not in settings_cols:
            conn.execute(
                text(
                    "CREATE TABLE settings_new ("
                    "user_id INTEGER PRIMARY KEY, "
                    "wake_up_time TIME NOT NULL, "
                    "timezone VARCHAR(64) NOT NULL)"
                )
            )
            conn.execute(
                text(
                    "INSERT INTO settings_new (user_id, wake_up_time, timezone) "
                    "SELECT :uid, wake_up_time, timezone FROM settings WHERE id = 1"
                ),
                {"uid": legacy_user_id},
            )
            conn.execute(text("DROP TABLE settings"))
            conn.execute(text("ALTER TABLE settings_new RENAME TO settings"))

    _set_version(engine, SCHEMA_VERSION)
    logger.info("Migration complete")
