"""The program as it was before the environment changed. It worked against API v1."""


def city_of(response: dict) -> str | None:
    match = response["match"]
    return match["city"] if match else None
