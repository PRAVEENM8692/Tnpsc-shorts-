"""Decides which video (slot 1-5) this run should build. Standard library only, so it runs in seconds.

The workflow wakes up every 30 minutes. A slot is DUE once its start time (IST) has passed, and is skipped if
it was already published today or has failed 3 times. So a late or skipped GitHub schedule is caught up on the
next wake-up instead of the video being lost."""
import datetime as dt
import json
import os
from zoneinfo import ZoneInfo

START = {1: 8.0, 2: 10.5, 3: 13.0, 4: 15.5, 5: 18.0}   # IST hours
LAST_HOUR = 22.0

now = dt.datetime.now(ZoneInfo("Asia/Kolkata"))
h = now.hour + now.minute / 60
today = now.strftime("%Y%m%d")
try:
    hist = json.load(open("history.json", encoding="utf-8"))
except Exception:
    hist = {}
done = set(hist.get("done", {}).get(today, []))
tries = hist.get("tries", {})

if os.environ.get("EVENT") == "workflow_dispatch":
    slot = (os.environ.get("INPUT_SLOT") or "1").strip()
else:
    due = [k for k, st in START.items()
           if st <= h < LAST_HOUR and k not in done and tries.get(f"{today}-{k}", 0) < 3]
    slot = str(min(due)) if due else ""

print(f"IST {now:%H:%M}  done today: {sorted(done)}  -> slot to build: {slot or 'none'}")
with open(os.environ["GITHUB_OUTPUT"], "a") as f:
    f.write(f"slot={slot}\n")
