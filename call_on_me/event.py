import dataclasses
import datetime
import urllib.parse
from typing import Optional

import arrow


def start_of_day(date: arrow.Arrow) -> arrow.Arrow:
    return date.replace(hour=0, minute=0, second=0, microsecond=0)


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

    def is_same_day(self) -> bool:
        return self.end is None or (self.end - self.start) < datetime.timedelta(hours=8)

    def days(self) -> list[arrow.Arrow]:
        if self.is_same_day():
            return [start_of_day(self.start)]

        days = []
        current = start_of_day(self.start)
        while current < self.end:
            days.append(current)
            current = current.shift(days=+1)

        return days

    def formatted_dates(self) -> list[str]:
        return [d.format("YYYY-MM-DD") for d in self.days()]

    def maps_link(self) -> str:
        base_link = "https://www.google.com/maps/search/?"
        params = {"api": 1, "query": self.location}
        return base_link + urllib.parse.urlencode(params)

    def print_date(self):
        if self.is_same_day():
            return self.start.format("MMMM Do")
        elif self.start.month == self.end.month:
            start = self.start.format("MMMM Do")
            end = self.end.format("Do")
            return f"{start} - {end}"
        else:
            start = self.start.format("MMMM Do")
            end = self.end.format("MMMM Do")
            return f"{start} - {end}"
