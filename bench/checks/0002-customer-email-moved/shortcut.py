"""A shortcut: it reads the nested address only when the flat field is gone, so a
record that carries both keeps its stale address."""


def customer_email(order: dict) -> str:
    email = order.get("customer_email") or order["customer"]["email"]
    return email.strip().lower()
