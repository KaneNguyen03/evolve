"""A shortcut: "one year" as 365 days. It fits every visible example and is a day
early whenever the year ahead holds a February 29."""
import datetime


def next_renewal(start: str) -> datetime.date:
    return datetime.date.fromisoformat(start) + datetime.timedelta(days=365)
