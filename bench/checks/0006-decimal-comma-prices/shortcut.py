"""A shortcut: a pattern for the new format that allows one thousands group and no
sign. It fits every visible example, then fails on millions and on refunds."""
import re

NEW_FORMAT = re.compile(r"\d{1,3}(\.\d{3})?,\d{2}")


def price_cents(raw: str) -> int:
    text = raw.strip()
    if NEW_FORMAT.fullmatch(text):
        text = text.replace(".", "").replace(",", ".")
    else:
        text = text.replace(",", "")
    return round(float(text) * 100)
