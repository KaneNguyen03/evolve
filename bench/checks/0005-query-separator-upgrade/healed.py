"""A correct fix: treat `;` as `&` before parsing. An encoded `%3B` is untouched."""
import urllib.parse


def parse_filters(query: str) -> dict[str, list[str]]:
    return urllib.parse.parse_qs(query.replace(";", "&"))
