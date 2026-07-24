from __future__ import annotations

from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from bot.models import Event, ReminderLog, Settings

MEAL_LABELS = {
    "breakfast": "завтрак",
    "snack": "перекус",
    "lunch": "обед",
    "dinner": "ужин",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def parse_hhmm(value: str) -> time:
    hour, minute = value.split(":")
    return time(int(hour), int(minute))


def format_local_time(dt_utc: datetime, tz_name: str) -> str:
    aware = dt_utc.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(tz_name))
    return aware.strftime("%H:%M")


def format_local_iso(dt_utc: datetime, tz_name: str) -> str:
    aware = dt_utc.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(tz_name))
    return aware.isoformat(timespec="minutes")


class Repository:
    def __init__(self, session_factory: sessionmaker, timezone_name: str, wake_up_time: str):
        self.session_factory = session_factory
        self.timezone_name = timezone_name
        self.default_wake_up = wake_up_time

    def _session(self) -> Session:
        return self.session_factory()

    def ensure_settings(self) -> None:
        with self._session() as session:
            settings = session.get(Settings, 1)
            if settings is None:
                session.add(
                    Settings(
                        id=1,
                        wake_up_time=parse_hhmm(self.default_wake_up),
                        timezone=self.timezone_name,
                    )
                )
                session.commit()

    def get_settings(self) -> Settings:
        with self._session() as session:
            settings = session.get(Settings, 1)
            if settings is None:
                self.ensure_settings()
                settings = session.get(Settings, 1)
            assert settings is not None
            session.expunge(settings)
            return settings

    def update_wake_up_time(self, value: str) -> str:
        parsed = parse_hhmm(value)
        with self._session() as session:
            settings = session.get(Settings, 1)
            if settings is None:
                settings = Settings(id=1, wake_up_time=parsed, timezone=self.timezone_name)
                session.add(settings)
            else:
                settings.wake_up_time = parsed
            session.commit()
            return parsed.strftime("%H:%M")

    def add_hunger(self, level: int) -> Event:
        with self._session() as session:
            event = Event(
                created_at=utc_now(),
                event_type="hunger",
                hunger_level=level,
            )
            session.add(event)
            session.commit()
            session.refresh(event)
            session.expunge(event)
            return event

    def add_meal(self, meal_type: str, hunger_before: int, satiety_after: int) -> Event:
        with self._session() as session:
            event = Event(
                created_at=utc_now(),
                event_type="meal",
                meal_type=meal_type,
                hunger_before=hunger_before,
                satiety_after=satiety_after,
            )
            session.add(event)
            session.commit()
            session.refresh(event)
            session.expunge(event)
            return event

    def list_events(self) -> list[Event]:
        with self._session() as session:
            events = list(session.scalars(select(Event).order_by(Event.created_at.asc())))
            for event in events:
                session.expunge(event)
            return events

    def count_events(self) -> int:
        with self._session() as session:
            return len(list(session.scalars(select(Event.id))))

    def last_activity_at(self) -> datetime | None:
        with self._session() as session:
            event = session.scalars(select(Event).order_by(Event.created_at.desc()).limit(1)).first()
            return event.created_at if event else None

    def last_morning_at(self) -> datetime | None:
        with self._session() as session:
            row = session.scalars(
                select(ReminderLog)
                .where(ReminderLog.reminder_type == "morning")
                .order_by(ReminderLog.sent_at.desc())
                .limit(1)
            ).first()
            return row.sent_at if row else None

    def inactivity_reminders_since(self, since: datetime | None) -> list[ReminderLog]:
        with self._session() as session:
            stmt = select(ReminderLog).where(
                ReminderLog.reminder_type.in_(("inactivity_1", "inactivity_2"))
            )
            if since is not None:
                stmt = stmt.where(ReminderLog.sent_at >= since)
            rows = list(session.scalars(stmt.order_by(ReminderLog.sent_at.asc())))
            for row in rows:
                session.expunge(row)
            return rows

    def last_inactivity_at(self) -> datetime | None:
        with self._session() as session:
            row = session.scalars(
                select(ReminderLog)
                .where(ReminderLog.reminder_type.in_(("inactivity_1", "inactivity_2")))
                .order_by(ReminderLog.sent_at.desc())
                .limit(1)
            ).first()
            return row.sent_at if row else None

    def log_reminder(self, reminder_type: str) -> ReminderLog:
        with self._session() as session:
            row = ReminderLog(sent_at=utc_now(), reminder_type=reminder_type)
            session.add(row)
            session.commit()
            session.refresh(row)
            session.expunge(row)
            return row
