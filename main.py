import concurrent.futures
import glob
import pathlib
import shutil
import subprocess

import arrow
import jinja2

from call_on_me import ical_parser, gsheet_parser, image_assets, event_list_context
from call_on_me.file_asset import FileAsset
from call_on_me.event import start_of_day


TRAVEL_EVENTS_ICAL_URL = "https://calendar.google.com/calendar/ical/5262e85049fae4cd0e93fecf91b6686f5c6c1c4f6a8774619c96d72202783b3e%40group.calendar.google.com/public/basic.ics"
LOCAL_EVENTS_ICAL_URL = "https://calendar.google.com/calendar/ical/danceiowacity%40gmail.com/public/basic.ics"
ZOUK_ICAL_URL = "https://calendar.google.com/calendar/ical/iowazoukdance%40gmail.com/public/basic.ics"
WEST_COAST_ICAL_URL = "https://calendar.google.com/calendar/ical/c_194368077c66b682a49c7b950f4e9b6036f5cdcecee74dca3a013aa0ac5c3ea7%40group.calendar.google.com/public/basic.ics"
TANGO_ICAL_URL = "https://calendar.google.com/calendar/ical/21e7dd52f1a988e3fac57bc226b659b21858c2d8c141ddcbd3ee2255861e6aac%40group.calendar.google.com/public/basic.ics"


BALLROOM_ICAL_URL = """https://calendar.google.com/calendar/ical/corridordance%40gmail.com/public/basic.ics"""

S3_OUT_DIR = "/tmp/out/"


def sync(out_dir: str):
    """aws s3 sync out/ s3://call-on-me-file-host --delete --acl public-read"""
    sync1 = subprocess.run(
        [
            "aws",
            "s3",
            "sync",
            out_dir,
            "s3://call-on-me-file-host",
            "--delete",
            "--exclude",
            "*.*",
            "--include",
            "*.html",
            "--acl",
            "public-read",
            "--cache-control",
            "no-cache, max-age=0",
        ]
    )
    print(sync1)

    sync2 = subprocess.run(
        [
            "aws",
            "s3",
            "sync",
            out_dir,
            "s3://call-on-me-file-host",
            "--delete",
            "--include",
            "*.*",
            "--exclude",
            "*.html",
            "--acl",
            "public-read",
            "--cache-control",
            "public, max-age=315360000",
        ]
    )
    print(sync2)


def do_the_thing(use_local_events=False, upload=False):
    out_dir = S3_OUT_DIR if upload else "out/"
    start_at = start_of_day(arrow.now(tz="America/Chicago")).replace(day=1)

    if use_local_events:
        with open("example-calendars/gsheet.csv") as f:
            csv_events = f.read()
    else:
        csv_events = gsheet_parser.gsheet_csv()

    events = gsheet_parser.parse_gsheet(csv_events, start_at)

    shutil.rmtree(out_dir, ignore_errors=True)
    pathlib.Path(f"{out_dir}/assets").mkdir(parents=True, exist_ok=True)

    assets = {}
    for file_path_str in glob.iglob("templates/assets/*"):
        path = pathlib.Path(file_path_str)
        if path.suffix in [".jpg", ".jpeg", ".webp"]:
            key = path.stem
            image_asset = image_assets.resize(str(path))
            assets[key] = image_asset
            image_asset.write(out_dir)
        else:
            asset = FileAsset(file_path_str)
            asset.write(out_dir)
            assets[asset.key] = asset

    shutil.copy2("templates/share-image.jpg", out_dir + "assets")
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))

    pathlib.Path(f"{out_dir}/sweetcorn").mkdir(parents=True, exist_ok=True)
    with open(f"{out_dir}/sweetcorn/index.html", "w+") as f:
        template = template_env.get_template("sweetcorn.html")
        f.write(template.render(events=events, assets=assets))

    with open(f"{out_dir}/swing.html", "w+") as f:
        template = template_env.get_template("swing-index.html")
        f.write(template.render(events=events, assets=assets))

    if use_local_events:
        with open("example-calendars/travel.ics") as f:
            ical_calendars = [(f.read(), "SWING")]
    else:
        ical_calendars = fetch_calendars()

    for ical, dance_type in ical_calendars:
        events += ical_parser.parse_ical(ical, start_at, dance_type)

    for event in events:
        if "salsa" in event.name.lower():
            event.dance_types = ["SALSA"]

    events.sort(key=lambda e: e.start)
    filters = {
        "dance_types": {
            "SWING": "Swing Dance",
            "SALSA": "Salsa/Bachata",
            "TANGO": "Tango",
            "ZOUK": "Zouk",
            "WEST_COAST": "West Coast",
            "BALLROOM": "Ballroom",
            "LINE_DANCING": "Line Dancing",
            "STREET": "Street/Hip Hop",
            "SAMBA": "Samba",
        }
    }

    months_to_build = 12
    current = start_of_day(arrow.now(tz="America/Chicago")).replace(day=1)

    months: list[tuple[int, int]] = []
    for i in range(12):
        months.append((current.year, current.month))
        current = current.shift(months=+1)

    for index, (year, month) in enumerate(months, start=1):
        is_first = index == 1
        is_second = index == 2
        is_last = index == months_to_build

        event_context = event_list_context.build_context(
            year, month, events, is_first, is_last
        )

        if is_second:
            event_context.prev_link = "/"

        padded_month = str(month).zfill(2)
        relative_path = (
            f"index.html" if is_first else f"{year}/{padded_month}/index.html"
        )

        file_path = out_dir + relative_path
        pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w+") as f:
            template = template_env.get_template("events.html")
            f.write(
                template.render(
                    event_context=event_context,
                    assets=assets,
                    filters=filters,
                )
            )

    with open(f"{out_dir}/add-event.html", "w+") as f:
        template = template_env.get_template("add-event.html")
        f.write(template.render(events=events))

    if upload:
        sync(out_dir)


def fetch_calendars():
    ical_calendar_config = [
        (LOCAL_EVENTS_ICAL_URL, "SWING"),
        (BALLROOM_ICAL_URL, "BALLROOM"),
        (ZOUK_ICAL_URL, "ZOUK"),
        (WEST_COAST_ICAL_URL, "WEST_COAST"),
        (TANGO_ICAL_URL, "TANGO"),
    ]
    urls = [r[0] for r in ical_calendar_config]
    dance_types = [r[1] for r in ical_calendar_config]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        ical_calendars = zip(executor.map(ical_parser.from_url, urls), dance_types)
    return ical_calendars


def handler(_, __):
    do_the_thing(use_local_events=False, upload=True)


if __name__ == "__main__":
    do_the_thing(use_local_events=False, upload=False)
