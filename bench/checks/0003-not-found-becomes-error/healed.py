"""A correct fix: only NOT_FOUND means "no such address"; any other error raises."""


def city_of(response: dict) -> str | None:
    error = response.get("error")
    if error is not None:
        if error.get("code") == "NOT_FOUND":
            return None
        raise RuntimeError(f"geocoding failed: {error.get('code')}")
    match = response["match"]
    return match["city"] if match else None
