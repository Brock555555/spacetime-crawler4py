"""
I believe this was a tester file for thread implementation that never got removed
"""





import re
from datetime import datetime, timedelta

LOG_PATH = "worker.log.txt"   # change to your actual log filename
MIN_DELAY_MS = 500

# Example line:
# 2026-02-07 05:40:10,652 - Worker-2 - INFO - Downloaded ...
line_re = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - Worker-(?P<id>\d+) - INFO - Downloaded"
)

def parse_ts(ts_str: str) -> datetime:
    return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S,%f")

last_ts_per_worker = {}
violations = []

with open(LOG_PATH, "r", encoding="utf-8") as f:
    for line in f:
        m = line_re.match(line)
        if not m:
            continue

        ts = parse_ts(m.group("ts"))
        wid = int(m.group("id"))

        if wid in last_ts_per_worker:
            delta = ts - last_ts_per_worker[wid]
            delta_ms = delta.total_seconds() * 1000

            if delta_ms < MIN_DELAY_MS:
                violations.append((wid, last_ts_per_worker[wid], ts, delta_ms, line.strip()))

        last_ts_per_worker[wid] = ts

if not violations:
    print(f"OK: no per-thread delay violations below {MIN_DELAY_MS} ms.")
else:
    print(f"Found {len(violations)} violations (< {MIN_DELAY_MS} ms):")
    for wid, prev_ts, ts, delta_ms, line in violations:
        print(f"Worker-{wid}: {prev_ts} -> {ts} = {delta_ms:.1f} ms")
        print(f"  line: {line}")
