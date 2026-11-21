"""The program as it was before the environment changed. It worked until the runtime upgrade."""
import urllib.parse


def parse_filters(query: str) -> dict[str, list[str]]:
    return urllib.parse.parse_qs(query)
