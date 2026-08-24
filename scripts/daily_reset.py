#!/usr/bin/env python
"""Run the daily reset for every player.

The iOS app calls POST /system/daily-reset on launch, which covers the common
case. Run this from cron as well if you want penalties to land on time even
when the app is not opened for days.

    */15 * * * * cd /srv/system && .venv/bin/python -m scripts.daily_reset

Safe to run at any frequency: the reset is idempotent within a player's local
day, so extra runs do nothing. Running at least hourly is worthwhile because
players in different timezones cross midnight at different moments.
"""

import sys

from app.config import get_settings
from app.db import SessionLocal
from app.services.daily import run_daily_reset_for_all


def main() -> int:
    settings = get_settings()
    with SessionLocal() as db:
        results = run_daily_reset_for_all(db, settings)

    failed = sum(r.failed_count for r in results.values())
    spawned = sum(r.spawned_count for r in results.values())
    lost = sum(r.total_exp_lost for r in results.values())

    print(
        f"players={len(results)} failed={failed} spawned={spawned} exp_lost={lost}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
