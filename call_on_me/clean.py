import re


def _linkify(match: re.Match) -> str:
    prep = match.group("prep")
    link = match.group("url")
    return f'{prep}<a href="{link}">{link}</a> '


link_regex = re.compile(r"(?P<prep>^|[^\">])(?P<url>https?://[^\s<]+)")


def clean_links(html: str) -> str:
    return link_regex.sub(_linkify, html)
