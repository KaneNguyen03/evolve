"""A correct fix: same month and day next year, and February 29 becomes February 28."""
import datetime


def next_renewal(start: str) -> datetime.date:
    day = datetime.date.fromisoformat(start)
    try:
        return day.replace(year=day.year + 1)
    except ValueError:
        return day.replace(year=day.year + 1, day=28)
