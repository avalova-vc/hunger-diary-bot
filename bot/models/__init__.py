from __future__ import annotations

from datetime import datetime, time

from sqlalchemy import DateTime, Integer, String, Time, create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    wake_up_time: Mapped[time] = mapped_column(Time, nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(16), nullable=False)
    hunger_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    meal_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    hunger_before: Mapped[int | None] = mapped_column(Integer, nullable=True)
    satiety_after: Mapped[int | None] = mapped_column(Integer, nullable=True)
    meal_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ReminderLog(Base):
    __tablename__ = "reminder_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    reminder_type: Mapped[str] = mapped_column(String(32), nullable=False)


def create_session_factory(db_path: str):
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    Base.metadata.create_all(engine)
    existing = {column["name"] for column in inspect(engine).get_columns("events")}
    if "meal_time" not in existing:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE events ADD COLUMN meal_time DATETIME"))
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)
