"""The program as it was before the environment changed. It worked for three years."""


def price_cents(raw: str) -> int:
    return round(float(raw.strip().replace(",", "")) * 100)
