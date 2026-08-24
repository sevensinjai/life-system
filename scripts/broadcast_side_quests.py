#!/usr/bin/env python
"""Send every side quest whose broadcast time has arrived.

Nothing else dispatches broadcasts — a scheduled side quest sits SCHEDULED
until this runs, so put it on the same cron as the daily reset:

    */15 * * * * cd /srv/system && .venv/bin/python -m scripts.broadcast_side_quests

Safe at any frequency. Offers are unique per (side quest, player), so a second
run reaches only the players the first one missed — someone who opted in an
hour late, or who was at their weekly cap until now.
"""

import sys

from app.config import get_settings
from app.db import SessionLocal
from app.services.side_quests import close_finished_broadcasts, dispatch_due


def main() -> int:
    get_settings()
    with SessionLocal() as db:
        results = dispatch_due(db)
        closed = close_finished_broadcasts(db)
        db.commit()

    offered = sum(r.offered_count for r in results)
    skipped = sum(r.skipped_count for r in results)

    print(
        f"broadcasts={len(results)} offers={offered} "
        f"skipped={skipped} closed={closed}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
