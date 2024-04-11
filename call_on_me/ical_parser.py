import datetime
import re

import arrow
import lxml.etree
import lxml.html
import ical.calendar_stream
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


def make_id(e):
    return e.uid + str(e.start)


def _process_html(html: str) -> str:
    if not html:
        return ""
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

    a: str = lxml.etree.tostring(
        root, encoding="unicode", method="xml", pretty_print=True
    )
    return a.removeprefix("<div>").removesuffix("</div>")


def parse_ical(raw_ical: str, start_at: arrow.Arrow, dance_type: str) -> list[Event]:
    calendar = ical.calendar_stream.IcsCalendarStream.calendar_from_ics(raw_ical)

    raw_events = calendar.timeline.active_after(
        datetime.date(start_at.year, start_at.month, start_at.day)
    )

    events = []
    count = 0
    ids = set()
    for rw in raw_events:
        count += 1

        if make_id(rw) in ids:
            continue

        ids.add(make_id(rw))

        if count > 100:
            break

        start = arrow.get(rw.dtstart)
        end = arrow.get(rw.dtend)

        events.append(
            Event(
                rw.uid,
                rw.summary,
                _process_html(rw.description),
                rw.location,
                convert_start_end_dates(start, end)[0],
                convert_start_end_dates(start, end)[1],
                source="travel_calendar",
                dance_types=[dance_type],
            )
        )

    return events
