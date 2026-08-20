from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import case, func, select
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


def event_effective_at(event: Event) -> datetime:
    if event.event_type == "meal" and event.ate_at is not None:
        return event.ate_at
    return event.created_at


def _effective_at_column():
    return case((Event.ate_at.isnot(None), Event.ate_at), else_=Event.created_at)


def meal_datetime_from_offset(minutes_ago: int) -> datetime:
    return utc_now() - timedelta(minutes=minutes_ago)


def meal_datetime_from_hhmm(value: str, tz_name: str) -> datetime:
    parsed = parse_hhmm(value)
    local_now = datetime.now(ZoneInfo(tz_name))
    candidate = local_now.replace(
        hour=parsed.hour,
        minute=parsed.minute,
        second=0,
        microsecond=0,
    )
    if candidate > local_now:
        candidate -= timedelta(days=1)
    return candidate.astimezone(timezone.utc).replace(tzinfo=None)


class Repository:
    def __init__(self, session_factory: sessionmaker, timezone_name: str):
        self.session_factory = session_factory
        self.timezone_name = timezone_name

    def _session(self) -> Session:
        return self.session_factory()

    def ensure_settings(self, user_id: int, default_wake_up: str) -> None:
        with self._session() as session:
            settings = session.get(Settings, user_id)
            if settings is None:
                session.add(
                    Settings(
                        user_id=user_id,
                        wake_up_time=parse_hhmm(default_wake_up),
                        timezone=self.timezone_name,
                    )
                )
                session.commit()

    def get_settings(self, user_id: int, *, default_wake_up: str = "08:00") -> Settings:
        with self._session() as session:
            settings = session.get(Settings, user_id)
            if settings is None:
                self.ensure_settings(user_id, default_wake_up)
                settings = session.get(Settings, user_id)
            assert settings is not None
            session.expunge(settings)
            return settings

    def update_wake_up_time(self, user_id: int, value: str) -> str:
        parsed = parse_hhmm(value)
        with self._session() as session:
            settings = session.get(Settings, user_id)
            if settings is None:
                settings = Settings(
                    user_id=user_id,
                    wake_up_time=parsed,
                    timezone=self.timezone_name,
                )
                session.add(settings)
            else:
                settings.wake_up_time = parsed
            session.commit()
            return parsed.strftime("%H:%M")

    def add_hunger(self, user_id: int, level: int) -> Event:
        with self._session() as session:
            event = Event(
                user_id=user_id,
                created_at=utc_now(),
                event_type="hunger",
                hunger_level=level,
            )
            session.add(event)
            session.commit()
            session.refresh(event)
            session.expunge(event)
            return event

    def add_meal(
        self,
        user_id: int,
        meal_type: str,
        hunger_before: int,
        satiety_after: int,
        ate_at: datetime,
    ) -> Event:
        with self._session() as session:
            event = Event(
                user_id=user_id,
                created_at=utc_now(),
                event_type="meal",
                meal_type=meal_type,
                hunger_before=hunger_before,
                satiety_after=satiety_after,
                ate_at=ate_at,
            )
            session.add(event)
            session.commit()
            session.refresh(event)
            session.expunge(event)
            return event

    def list_events(self, user_id: int) -> list[Event]:
        with self._session() as session:
            events = list(
                session.scalars(
                    select(Event)
                    .where(Event.user_id == user_id)
                    .order_by(_effective_at_column().asc())
                )
            )
            for event in events:
                session.expunge(event)
            return events

    def count_events(self, user_id: int) -> int:
        with self._session() as session:
            count = session.scalar(
                select(func.count()).select_from(Event).where(Event.user_id == user_id)
            )
            return int(count or 0)

    def last_activity_at(self, user_id: int) -> datetime | None:
        with self._session() as session:
            event = session.scalars(
                select(Event)
                .where(Event.user_id == user_id)
                .order_by(_effective_at_column().desc())
                .limit(1)
            ).first()
            return event_effective_at(event) if event else None

    def last_morning_at(self, user_id: int) -> datetime | None:
        with self._session() as session:
            row = session.scalars(
                select(ReminderLog)
                .where(
                    ReminderLog.user_id == user_id,
                    ReminderLog.reminder_type == "morning",
                )
                .order_by(ReminderLog.sent_at.desc())
                .limit(1)
            ).first()
            return row.sent_at if row else None

    def inactivity_reminders_since(self, user_id: int, since: datetime | None) -> list[ReminderLog]:
        with self._session() as session:
            stmt = select(ReminderLog).where(
                ReminderLog.user_id == user_id,
                ReminderLog.reminder_type.in_(("inactivity_1", "inactivity_2")),
            )
            if since is not None:
                stmt = stmt.where(ReminderLog.sent_at >= since)
            rows = list(session.scalars(stmt.order_by(ReminderLog.sent_at.asc())))
            for row in rows:
                session.expunge(row)
            return rows

    def log_reminder(self, user_id: int, reminder_type: str) -> ReminderLog:
        with self._session() as session:
            row = ReminderLog(
                user_id=user_id,
                sent_at=utc_now(),
                reminder_type=reminder_type,
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            session.expunge(row)
            return row
