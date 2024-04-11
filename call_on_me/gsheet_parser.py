import csv
import dataclasses
import io
import typing
import uuid
from typing import Optional

import arrow
import requests

from .event import Event


URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQPkGgjkwVujj70fFVeNjE1JSYZg5_x79YOYvReLNMRonBCGfp5kl1hFL5Au1NJZr0S7NoW7fiqvh0k/pub?output=csv"


@dataclasses.dataclass
class _CsvEvent:
    timestamp: Optional[str]
    title: Optional[str]
    description: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    name: Optional[str]
    email: Optional[str]
    location: Optional[str]
    dance_types: list[str]

    @staticmethod
    def from_dict(d) -> typing.Optional["_CsvEvent"]:
        if not d.get("Timestamp", None) or d.get("Display In Site", None) != "TRUE":
            return None

        dance_types = d["Type of Dance"].split(", ")
        dance_types = list(map(str.upper, dance_types))
        return _CsvEvent(
            timestamp=d.get("Timestamp"),
            title=d.get("Event Title"),
            description=d.get("Event Description"),
            start_date=d.get("Event Start Date"),
            end_date=d.get("Event End Date (optional)"),
            name=d.get("Your Name (will not be shared)"),
            email=d.get("Your Email (will not be shared)"),
            location=d.get("Event Location"),
            dance_types=dance_types,
        )


def _csv_event_to_event(csv_event: _CsvEvent) -> Event:
    start_date = arrow.get(csv_event.start_date, "M/D/YYYY").replace(
        tzinfo="America/Chicago"
    )

    end_date = (
        arrow.get(csv_event.end_date, "M/D/YYYY").replace(tzinfo="America/Chicago")
        if csv_event.end_date
        else None
    )

    description = csv_event.description.replace("\n", "<br>")
    description = f"<div>{description}</div>"

    return Event(
        location=csv_event.location,
        name=csv_event.title,
        description=description,
        start=start_date,
        end=end_date,
        dance_types=csv_event.dance_types,
        source="gform",
        id=str(uuid.uuid4()),
    )


def file_csv(path: str) -> str:
    with open(path) as f:
        return f.read()


def gsheet_csv():
    response = requests.get(URL)
    return response.content.decode("utf-8")


def parse_gsheet(event_csv: str, start_at: arrow.Arrow) -> list[Event]:
    io_like = io.StringIO(event_csv)
    lines = csv.DictReader(io_like)
    csv_events = list(map(_CsvEvent.from_dict, lines))
    csv_events = [cv for cv in csv_events if cv and not cv.title.startswith("TEST")]
    events = list(map(_csv_event_to_event, csv_events))
    return [e for e in events if e.start >= start_at]
