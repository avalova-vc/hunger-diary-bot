from __future__ import annotations

from datetime import datetime, time

from sqlalchemy import DateTime, Index, Integer, String, Time, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from bot.migrations import run_migrations


class Base(DeclarativeBase):
    pass


class Settings(Base):
    __tablename__ = "settings"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    wake_up_time: Mapped[time] = mapped_column(Time, nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False)


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (Index("ix_events_user_created", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(16), nullable=False)
    hunger_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    meal_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    hunger_before: Mapped[int | None] = mapped_column(Integer, nullable=True)
    satiety_after: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ate_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ReminderLog(Base):
    __tablename__ = "reminder_log"
    __table_args__ = (Index("ix_reminder_log_user_sent", "user_id", "sent_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    reminder_type: Mapped[str] = mapped_column(String(32), nullable=False)


def create_session_factory(db_path: str, legacy_user_id: int, all_user_ids: list[int]):
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    run_migrations(engine, legacy_user_id, all_user_ids)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)
