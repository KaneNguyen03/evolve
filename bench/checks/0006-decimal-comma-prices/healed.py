"""A correct fix: with two decimals guaranteed, the third character from the end
says which format this is."""


def price_cents(raw: str) -> int:
    text = raw.strip()
    if text[-3:-2] == ",":
        text = text.replace(".", "").replace(",", ".")
    else:
        text = text.replace(",", "")
    return round(float(text) * 100)
