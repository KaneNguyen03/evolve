"""The program as it was before the environment changed. It worked since the first release."""


def customer_email(order: dict) -> str:
    return order["customer_email"].strip().lower()
