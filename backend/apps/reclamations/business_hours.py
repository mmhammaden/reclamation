"""
Business hours utilities for RG-01: 72 working hours SLA.
Working hours: 08:00 - 18:00, Monday-Friday (excluding weekends).
Holidays list can be extended via Django setting.
"""
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone

# Default working hours
WORKDAY_START = 8   # 08:00
WORKDAY_END = 18    # 18:00
WORKING_HOURS_PER_DAY = WORKDAY_END - WORKDAY_START  # 10 hours


def get_holidays():
    """Return set of holiday dates (as date objects) from settings."""
    holidays = getattr(settings, 'HOLIDAYS', [])
    if holidays:
        return set(holidays)
    return set()


def is_working_day(dt):
    """Check if datetime falls on a working day (Mon-Fri, not a holiday)."""
    if dt.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    holidays = get_holidays()
    if dt.date() in holidays:
        return False
    return True


def next_working_day(dt):
    """Move to the next working day at WORKDAY_START."""
    dt = dt.replace(hour=WORKDAY_START, minute=0, second=0, microsecond=0)
    while not is_working_day(dt):
        dt += timedelta(days=1)
    return dt


def add_business_hours(start_dt, hours_to_add=72):
    """
    Add `hours_to_add` working hours to `start_dt`.
    Only counts hours during working days (08:00-18:00 Mon-Fri).
    """
    current = start_dt
    remaining = hours_to_add

    # If outside working hours on a working day, snap to next working hour
    if is_working_day(current):
        hour = current.hour
        if hour < WORKDAY_START:
            # Before workday starts -> move to start
            current = current.replace(hour=WORKDAY_START, minute=0, second=0, microsecond=0)
        elif hour >= WORKDAY_END:
            # After workday ends -> move to next working day start
            current = next_working_day(current + timedelta(days=1))
    else:
        # Weekend or holiday -> move to next working day start
        current = next_working_day(current)

    while remaining > 0:
        if not is_working_day(current):
            current = next_working_day(current)
            continue

        # Calculate remaining hours in this working day
        hours_left_today = WORKDAY_END - current.hour

        if remaining <= hours_left_today:
            # Can finish today
            current += timedelta(hours=remaining)
            remaining = 0
        else:
            # Consume all remaining hours today, move to next day
            remaining -= hours_left_today
            current = next_working_day(current + timedelta(days=1))

    return current


def is_past_business_deadline(deadline_dt):
    """
    Check if the current time has passed the business-hours deadline.
    """
    now = timezone.now()
    return now > deadline_dt