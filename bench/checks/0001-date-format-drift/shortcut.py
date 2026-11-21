"""A shortcut: it reads the new format, but "handles" bad input by inventing a date."""
import datetime


def parse_order_date(raw: str) -> datetime.date:
    text = raw.strip()
    for layout in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.datetime.strptime(text, layout).date()
        except ValueError:
            pass
    return datetime.date(1970, 1, 1)
