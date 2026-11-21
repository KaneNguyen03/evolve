"""A shortcut: it treats every error as "no such address", so a rate limit silently
turns known addresses into unknown ones."""


def city_of(response: dict) -> str | None:
    if "error" in response:
        return None
    match = response["match"]
    return match["city"] if match else None
