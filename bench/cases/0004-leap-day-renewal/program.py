"""The program as it was before the environment changed. It worked for every renewal until 2025."""
import datetime


def next_renewal(start: str) -> datetime.date:
    day = datetime.date.fromisoformat(start)
    return day.replace(year=day.year + 1)
