import itertools
import re

import arrow
import lxml.etree
import lxml.html
import ics
import requests

from .event import Event


NOW = arrow.now(tz="America/Chicago").replace(hour=17, minute=59).shift(days=-1)


def from_url(url: str) -> str:
    return requests.get(url).text


def convert_start_end_dates(start: arrow.Arrow, end: arrow.Arrow):
    is_all_day = start.hour == 0 and end.hour == 0
    if is_all_day:
        return start, end.to("America/Chicago")
    else:
        return start.to("America/Chicago"), end.to("America/Chicago")


def _linkify(match: re.Match) -> str:
    link = match.group(0).strip()
    return f' <a href="{link}">{link}</a> '


def _process_html(html: str) -> str:
    # don't judge me
    html = html.strip().removeprefix("<br>")
    html = f" {html} "
    html = re.sub(" https://.* ", _linkify, html)
    html = html.replace("\n\n", "<br><br>")
    html = re.sub("(<br>)+", "<br><br>", html)

    root = lxml.html.fragment_fromstring(html, create_parent="div")
    for elem in root.iter():
        if elem.tag == "a":
            elem.set("target", "_blank")
            elem.set("rel", "noopener")

    a = lxml.etree.tostring(root, encoding="unicode", method="xml", pretty_print=True)
    return a


def parse_ical(raw_ical: str, start_at: arrow.Arrow) -> list[Event]:
    calendar = ics.Calendar(raw_ical)
    event_iterator = calendar.timeline.start_after(start_at)
    raw_events = list(itertools.islice(event_iterator, 20))
    return [
        Event(
            rw.uid,
            rw.name,
            _process_html(rw.description),
            rw.location,
            convert_start_end_dates(rw.begin, rw.end)[0],
            convert_start_end_dates(rw.begin, rw.end)[1],
            source="travel_calendar",
            dance_types=["SWING"],
        )
        for rw in raw_events
    ]
