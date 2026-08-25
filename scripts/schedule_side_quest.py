#!/usr/bin/env python
"""Put the next written trial on the calendar for every constellation.

This is what makes the System speak "from time to time". Run it daily:

    0 9 * * * cd /srv/system && .venv/bin/python -m scripts.schedule_side_quest

Each constellation keeps its own rotation and is allowed one open trial at a
time, so a figure whose last trial is still running is skipped. Nobody is
flooded by this: what reaches a given player is decided by which
constellations they befriended and by their own weekly cap.

Pass a catalog code to send one specific trial instead:

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

        if code is not None:
            scheduled = broadcasting.schedule(db, broadcasting.entry_by_code(code))
            db.commit()
            print(f"scheduled {scheduled.entry.code}")
            return 0

        placed = broadcasting.schedule_due_constellations(db)
        db.commit()

        print(f"scheduled={len(placed)}")
        for item in placed:
            print(
                f"  {item.entry.constellation:16} {item.entry.code:38} "
                f"{item.entry.difficulty.value} "
                f"expires={item.side_quest.expires_at.isoformat()}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
