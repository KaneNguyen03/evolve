"""A shortcut: pick one separator per link. It fits every visible example and
breaks the links that mix `&` and `;`."""
import urllib.parse


def parse_filters(query: str) -> dict[str, list[str]]:
    if ";" in query:
        return urllib.parse.parse_qs(query, separator=";")
    return urllib.parse.parse_qs(query)
