import dataclasses
from typing import Optional

import arrow

from call_on_me.event import Event, start_of_day


@dataclasses.dataclass
class EventListContext:
    year: int
    month: int
    events: list[Event]
    events_by_day: dict[arrow.Arrow, list[Event]]
    prev_link: Optional[str] = None
    next_link: Optional[str] = None

    def month_name(self):
        return arrow.get(f"{self.year}-{self.month}-01").format("MMMM YYYY")

    def dance_types_on_day(self, day: arrow.Arrow) -> set[str]:
        events = self.events_by_day[day]
        return set(dt for event in events for dt in event.dance_types)

    def preselected_day(self) -> str:
        today = start_of_day(arrow.now("America/Chicago"))
        return today.format("YYYY-MM-DD")


def build_context(
    year: int, month: int, events: list[Event], first, last
) -> EventListContext:
    events = [
        e for e in events if any(d.year == year and d.month == month for d in e.days())
    ]
    events_by_day = {}
    month_start = arrow.get(f"{year}-{month}-1", tzinfo="America/Chicago")
    day = month_start.replace(day=1)
    while day.month == month_start.month:
        events_by_day[day] = []
        day = day.shift(days=1)

    for event in events:
        for date in event.formatted_dates():
            date_as_arrow = arrow.get(date, tzinfo="America/Chicago")
            if date_as_arrow in events_by_day:
                events_by_day[date_as_arrow].append(event)

    prev_link = month_start.shift(months=-1).format("/YYYY/MM/") if not first else None
    next_link = month_start.shift(months=+1).format("/YYYY/MM/") if not last else None

    return EventListContext(year, month, events, events_by_day, prev_link, next_link)
