from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from bot.repositories import MEAL_LABELS, Repository, format_local_iso


def export_events_to_csv(repo: Repository, user_id: int, exports_dir: Path) -> tuple[Path | None, int]:
    events = repo.list_events(user_id)
    if not events:
        return None, 0

    filename = exports_dir / f"hunger_diary_{date.today().isoformat()}.csv"
    with filename.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "id",
                "datetime",
                "event_type",
                "hunger_level",
                "meal_type",
                "hunger_before",
                "satiety_after",
            ],
        )
        writer.writeheader()
        for event in events:
            writer.writerow(
                {
                    "id": event.id,
                    "datetime": format_local_iso(event.created_at, repo.timezone_name),
                    "event_type": event.event_type,
                    "hunger_level": event.hunger_level if event.hunger_level is not None else "",
                    "meal_type": MEAL_LABELS.get(event.meal_type or "", event.meal_type or ""),
                    "hunger_before": event.hunger_before if event.hunger_before is not None else "",
                    "satiety_after": event.satiety_after if event.satiety_after is not None else "",
                }
            )
    return filename, len(events)
