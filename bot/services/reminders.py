from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from bot.repositories import Repository, utc_now


@dataclass
class ReminderDecision:
    kind: str | None  # morning | inactivity_1 | inactivity_2 | None


def _local_now(tz_name: str) -> datetime:
    return datetime.now(ZoneInfo(tz_name))


def is_quiet_hours(local_now: datetime, sleep_time: time, wake_up_time: time) -> bool:
    current = local_now.time().replace(second=0, microsecond=0)
    if sleep_time <= wake_up_time:
        return sleep_time <= current < wake_up_time
    return current >= sleep_time or current < wake_up_time


def decide_inactivity(repo: Repository, sleep_time: str) -> ReminderDecision:
    settings = repo.get_settings()
    local = _local_now(repo.timezone_name)
    sleep = time.fromisoformat(sleep_time)
    wake = settings.wake_up_time

    if is_quiet_hours(local, sleep, wake):
        return ReminderDecision(None)

    now = utc_now()
    last_activity = repo.last_activity_at()
    last_morning = repo.last_morning_at()

    # No morning yet and no activity — wait for first morning
    if last_morning is None and last_activity is None:
        return ReminderDecision(None)

    cycle_start = last_morning
    all_in_cycle = repo.inactivity_reminders_since(cycle_start)

    # New user record resets the inactivity chain
    if last_activity is not None:
        effective = [r for r in all_in_cycle if r.sent_at > last_activity]
    else:
        effective = list(all_in_cycle)

    count = len(effective)
    if count >= 2:
        return ReminderDecision(None)

    two_hours = timedelta(hours=2)

    if count == 0:
        if last_activity is not None:
            reference = last_activity
            if last_morning is not None and last_activity < last_morning:
                reference = last_morning
        else:
            reference = last_morning
        assert reference is not None
        if now - reference >= two_hours:
            return ReminderDecision("inactivity_1")
        return ReminderDecision(None)

    first = effective[-1]
    if now - first.sent_at >= two_hours:
        return ReminderDecision("inactivity_2")
    return ReminderDecision(None)


def should_send_morning(repo: Repository) -> bool:
    settings = repo.get_settings()
    local = _local_now(repo.timezone_name)
    wake = settings.wake_up_time

    current = local.time().replace(second=0, microsecond=0)
    if current != wake.replace(second=0, microsecond=0):
        return False

    last_morning = repo.last_morning_at()
    if last_morning is None:
        return True

    last_local = last_morning.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(repo.timezone_name))
    return last_local.date() != local.date()
