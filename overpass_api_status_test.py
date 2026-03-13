from datetime import datetime, timedelta
from pprint import pprint
import pytest

from overpass_api_status import parse_status_response


def test_response_no_endpoint_no_ratelimit_large_query_table() -> None:
    body = """\
Connected as: 175833359
Current time: 2026-03-13T17:11:38Z
Announced endpoint: none
Rate limit: 0
Currently running queries (pid, space limit, time limit, start time):
788103	536870912	25	2026-03-13T17:11:37Z
788055	536870912	60	2026-03-13T17:11:30Z
787742	536870912	30	2026-03-13T17:11:30Z
787791	536870912	180	2026-03-13T17:11:37Z
787885	536870912	10	2026-03-13T17:11:09Z
787862	536870912	10	2026-03-13T17:11:08Z
781662	536870912	900	2026-03-13T17:01:05Z
787790	536870912	45	2026-03-13T17:11:32Z
787017	536870912	90	2026-03-13T17:09:39Z
787739	536870912	25	2026-03-13T17:11:29Z
787856	536870912	25	2026-03-13T17:11:11Z
787818	536870912	25	2026-03-13T17:11:06Z
788086	536870912	180	2026-03-13T17:11:33Z
787747	536870912	45	2026-03-13T17:11:31Z
788106	536870912	180	2026-03-13T17:11:38Z
"""
    p = parse_status_response(body)
    assert p["connected_as"] == 175833359
    assert p["announced_endpoint"] == "none"
    assert p["rate_limit"] == 0
    assert p["available_slots"] == 0
    assert len(p["currently_running_queries"]) == 15


def test_available_slots_empty_table() -> None:
    body = """\
Connected as: 1823116064
Current time: 2026-03-13T17:13:36Z
Announced endpoint: lambert.openstreetmap.de/
Rate limit: 2
2 slots available now.
Currently running queries (pid, space limit, time limit, start time):
"""
    p = parse_status_response(body)
    assert p["connected_as"] == 1823116064
    assert p["announced_endpoint"] == "lambert.openstreetmap.de/"
    assert p["rate_limit"] == 2
    assert p["available_slots"] == 2
    assert len(p["currently_running_queries"]) == 0


@pytest.mark.parametrize("rate_limit", [0, 2])
@pytest.mark.parametrize("num_queries", [0, 10])
def test_status_combinations(rate_limit: int, num_queries: int) -> None:
    """Test every known output from Overpass-API:: public_status.cc"""
    # https://github.com/drolbr/Overpass-API/blob/master/src/overpass_api/dispatch/public_status.cc

    now = datetime.now()

    def to_date(t: datetime) -> str:
        # same format string used
        return now.strftime("%FT%TZ")

    r = [
        "Connected as: 1",
        f"Current time: {to_date(now)}",  # iso8601 with T and Z
        "Announced endpoint: none",  # str
        f"Rate limit: {rate_limit}",  # uint32
    ]

    # make a list of fake slots
    slot_starts_size = 2
    slot_starts: list[datetime] = list([
        now + timedelta(seconds=1+(k*2))
        for k in range(slot_starts_size)
    ])

    if slot_starts_size + num_queries < rate_limit:
        r.append(f"{rate_limit - slot_starts_size - num_queries} slots available now.")

    for slot in slot_starts:
        r.append(f"Slot available after: {to_date(slot)}, in {int((slot - now).total_seconds())} seconds")

    r.append(
        "Currently running queries (pid, space limit, time limit, start time):"
    )

    for query in range(num_queries):
        r.append(f"111{query}\t5555912\t{90+(10*query)}\t{to_date(now - timedelta(seconds=3 + (query*3)))}")

    body = "\n".join(r)

    print(body)
    p = parse_status_response(body)
    pprint(p, compact=False, sort_dicts=False, width=200)

    assert len(p["currently_running_queries"]) == num_queries
