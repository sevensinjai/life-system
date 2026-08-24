#!/usr/bin/env python
"""Put the next written trial on the calendar, occasionally.

This is what makes the System speak "from time to time". Run it daily:

    0 9 * * * cd /srv/system && .venv/bin/python -m scripts.schedule_side_quest

It does nothing while a broadcast is still open, so the sky stays quiet
between trials rather than stacking three at once. Pass a catalog code to send
a specific one instead of taking the next in rotation:

    .venv/bin/python -m scripts.schedule_side_quest xingtian.hundred

Scheduling is not sending. `scripts/broadcast_side_quests.py` is what puts a
scheduled trial in front of players when its moment arrives.
"""

import sys

from app.config import get_settings
from app.db import SessionLocal
from app.services import broadcasting


def main(argv: list[str]) -> int:
    get_settings()
    code = argv[1] if len(argv) > 1 else None

    with SessionLocal() as db:
        broadcasting.ensure_pantheon(db)

        if code is None and broadcasting.has_open_broadcast(db):
            db.commit()
            print("skipped: a side quest is already open")
            return 0

        if code is None:
            scheduled = broadcasting.schedule_next(db)
        else:
            scheduled = broadcasting.schedule(db, broadcasting.entry_by_code(code))

        if scheduled is None:
            print("skipped: every trial in the catalog is still resting")
            return 0

        db.commit()
        print(
            f"scheduled {scheduled.entry.code} "
            f"({scheduled.entry.constellation}) "
            f"expires={scheduled.side_quest.expires_at.isoformat()}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
