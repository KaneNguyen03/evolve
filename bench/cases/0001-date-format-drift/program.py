"""The program as it was before the environment changed. It worked for two years."""
import datetime


def parse_order_date(raw: str) -> datetime.date:
    return datetime.datetime.strptime(raw.strip(), "%Y-%m-%d").date()
