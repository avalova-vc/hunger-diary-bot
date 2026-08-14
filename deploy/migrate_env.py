#!/usr/bin/env python3
"""Upgrade /opt/hunger-bot/.env from single-user to multi-user format."""
from __future__ import annotations

import sys
from pathlib import Path


def parse_env(text: str) -> tuple[list[str], dict[str, str]]:
    lines = text.splitlines()
    data: dict[str, str] = {}
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return lines, data


def main() -> int:
    env_path = Path(sys.argv[1] if len(sys.argv) > 1 else "/opt/hunger-bot/.env")
    if not env_path.exists():
        print(f"Missing {env_path}", file=sys.stderr)
        return 1

    original = env_path.read_text(encoding="utf-8")
    lines, data = parse_env(original)

    if "ALLOWED_USER_IDS" in data:
        print("ALLOWED_USER_IDS already set — no env migration needed")
        return 0

    user_id = data.get("ALLOWED_USER_ID", "").strip()
    if not user_id:
        print("ALLOWED_USER_ID not found in .env", file=sys.stderr)
        return 1

    wake_up = data.get("WAKE_UP_TIME", "07:00").strip()
    inactivity = data.get("INACTIVITY_HOURS", "2").strip()

    drop_keys = {"ALLOWED_USER_ID", "WAKE_UP_TIME", "INACTIVITY_HOURS"}
    new_lines: list[str] = []
    for line in lines:
        key = line.split("=", 1)[0].strip() if "=" in line and not line.strip().startswith("#") else ""
        if key in drop_keys:
            continue
        new_lines.append(line)

    while new_lines and not new_lines[-1].strip():
        new_lines.pop()

    new_lines.extend(
        [
            "",
            f"ALLOWED_USER_IDS={user_id}",
            f"USER_{user_id}_WAKE_UP={wake_up}",
            f"USER_{user_id}_INACTIVITY_HOURS={inactivity}",
            "",
        ]
    )

    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"Migrated .env for user_id={user_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
