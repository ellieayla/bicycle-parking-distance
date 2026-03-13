#!/usr/bin/env python

from argparse import ArgumentParser
from datetime import datetime
from logging import getLogger
from typing import Required, TypedDict
from csv import DictReader
from urllib.request import Request, urlopen


logger = getLogger(__name__)


class RunningQuery(TypedDict):
    pid: int
    space_limit: int
    time_limit: int
    start_time: datetime


class Status(TypedDict):
    connected_as: int | None
    current_time: datetime | None
    announced_endpoint: str
    rate_limit: int | None
    available_slots: int
    currently_running_queries: Required[list[RunningQuery]]


def parse_status_response(response_body: str) -> Status:
    # https://github.com/drolbr/Overpass-API/blob/a0db4f392f744d5e1304331edbf542ef6d6ce2fa/src/overpass_api/dispatch/public_status.cc#L54

    # response_body is a sequence of key: value lines,
    # followed by a tab-seperated value table.

    connected_as = None
    current_time = None
    announced_endpoint = "none"
    rate_limit = None
    available_slots = 0

    iterable = iter(response_body.splitlines())

    for row in iterable:
        match row.partition(" "):
            case (slots, _, "slots available now.") if slots.isnumeric():
                available_slots = int(slots)
                continue
            case _:
                pass

        match row.partition(": "):
            case ("Connected as", _, o):
                connected_as = int(o)
            case ("Current time", _, t):
                current_time = datetime.fromisoformat(t)
            case ("Announced endpoint", _, e):
                announced_endpoint = e
            case ("Rate limit", _, r):
                rate_limit = int(r)
            case ("Slot available after", _, _):
                pass
            case ("Currently running queries (pid, space limit, time limit, start time):", "", ""):
                break  # done with loop, onto TSV.
            case (unknown_status_key, _, _):
                if unknown_status_key == "Currently running queries (pid, space limit, time limit, start time)":
                    print('wat')
                raise ValueError(unknown_status_key)

    tsv = DictReader(
        iterable,
        fieldnames=("pid", "space_limit", "time_limit", "start_time"),
        delimiter="\t",
        strict=True,
    )

    status = Status(
        connected_as=connected_as,
        current_time=current_time,
        announced_endpoint=announced_endpoint,
        rate_limit=rate_limit,
        available_slots=available_slots,
        currently_running_queries=list([
            RunningQuery(
                    pid=int(tsv_row["pid"]),
                    space_limit=int(tsv_row["space_limit"]),
                    time_limit=int(tsv_row["time_limit"]),
                    start_time=datetime.fromisoformat(tsv_row["start_time"]),
            )
            for tsv_row in tsv
        ])
    )

    for row in iterable:
        logger.warning(f"Unparsed {row=}")
    return status


def status_of_endpoint(url: str) -> Status:
    r = Request(
        url=url,
        headers={
            "User-Agent": "bicycle-parking-distance[status-check]",
        }
    )
    with urlopen(r) as response:
        body = response.read(5000)

    text = body.decode()

    return parse_status_response(text)


def main() -> int:
    p = ArgumentParser()
    p.add_argument("--endpoint", default="https://overpass-api.de/api/status")
    p.add_argument("--check-available-slots", action="store_true", help="Exit with status 0 if at least one slot is available, otherwise 1.")
    p.add_argument("--verbose", action="store_true", help="Dump the full status to stdout.")
    args = p.parse_args()

    url: str = args.endpoint

    status = status_of_endpoint(url)

    if args.verbose:
        print(status)

    if args.check_available_slots:
        if status["available_slots"] > 0:
            return 0
        else:
            return 1


    return 1




if __name__ == "__main__":
    raise SystemExit(main())
