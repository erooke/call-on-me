import dataclasses
import datetime
import urllib.parse
from typing import Optional

import arrow


def _is_same_day(start: arrow.Arrow, end: Optional[arrow.Arrow]):
    return end is None or (end - start) < datetime.timedelta(hours=8)


@dataclasses.dataclass
class Event:
    id: str
    name: str
    description: str
    location: str
    start: arrow.Arrow
    end: Optional[arrow.Arrow]
    source: str
    dance_types: list[str]

    def start_date(self):
        return self.start.format("dddd, MMMM Do")

    def maps_link(self) -> str:
        base_link = "https://www.google.com/maps/search/?"
        params = {"api": 1, "query": self.location}
        return base_link + urllib.parse.urlencode(params)

    def print_date(self):
        if _is_same_day(self.start, self.end):
            return self.start.format("MMMM Do")
        elif self.start.month == self.end.month:
            start = self.start.format("MMMM Do")
            end = self.end.format("Do")
            return f"{start} - {end}"
        else:
            start = self.start.format("MMMM Do")
            end = self.end.format("MMMM Do")
            return f"{start} - {end}"
