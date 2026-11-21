"""A correct fix: the nested address wins, the flat field is the fallback."""


def customer_email(order: dict) -> str:
    customer = order.get("customer") or {}
    email = customer["email"] if "email" in customer else order["customer_email"]
    return email.strip().lower()
