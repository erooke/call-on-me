import glob
import pathlib
import shutil
import subprocess

import arrow
import jinja2

from call_on_me import ical_parser, gsheet_parser, image_assets
from call_on_me.file_asset import FileAsset

ICAL_URL = "https://calendar.google.com/calendar/ical/5262e85049fae4cd0e93fecf91b6686f5c6c1c4f6a8774619c96d72202783b3e%40group.calendar.google.com/public/basic.ics"

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
    start_at = (
        arrow.now(tz="America/Chicago")
        # .replace(day=2)
        .replace(hour=17, minute=59).shift(days=-1)
    )

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

    if use_local_events:
        with open("example-calendars/travel.ics") as f:
            ical_events = f.read()
    else:
        ical_events = ical_parser.from_url(ICAL_URL)

    events += ical_parser.parse_ical(ical_events, start_at)
    events.sort(key=lambda e: e.start)
    filters = {"dance_types": ["SWING", "SALSA", "TANGO", "ZOUK", "WEST COAST"]}

    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))

    with open(f"{out_dir}/swing.html", "w+") as f:
        template = template_env.get_template("swing-index.html")
        f.write(template.render(events=events, assets=assets))

    with open(f"{out_dir}/index.html", "w+") as f:
        template = template_env.get_template("events.html")
        f.write(template.render(events=events, assets=assets, filters=filters))

    with open(f"{out_dir}/add-event.html", "w+") as f:
        template = template_env.get_template("add-event.html")
        f.write(template.render(events=events))

    if upload:
        sync(out_dir)


def handler(_, __):
    do_the_thing(use_local_events=False, upload=True)


if __name__ == "__main__":
    do_the_thing(use_local_events=True, upload=False)
