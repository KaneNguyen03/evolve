"""A correct fix: accept both formats, and keep rejecting what is not a date."""
import datetime


def parse_order_date(raw: str) -> datetime.date:
    text = raw.strip()
    for layout in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.datetime.strptime(text, layout).date()
        except ValueError:
            pass
    raise ValueError(f"not an order date: {raw!r}")
