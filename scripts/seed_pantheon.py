#!/usr/bin/env python
"""Load the written pantheon into the database.

Run once at setup, and again after any edit to `app/content/pantheon.py`:

    .venv/bin/python -m scripts.seed_pantheon

Idempotent, and matched on each constellation's `code`, so rewriting a name or
a voice updates the row in place and every player's history with that
constellation survives the edit.

Nothing is ever deleted. A constellation that has left the catalog is retired:
it stops issuing and stops being offered, and its rows — favor, friendships,
the side quests it already sent — are left exactly where they are.
"""

import sys

from app.config import get_settings
from app.db import SessionLocal
from app.services.constellations import seed_pantheon


def main() -> int:
    get_settings()
    with SessionLocal() as db:
        result = seed_pantheon(db)
        db.commit()

    print(
        f"created={result.created_count} updated={result.updated_count} "
        f"retired={result.retired_count}"
    )
    for code in result.created:
        print(f"  + {code}")
    for code in result.updated:
        print(f"  ~ {code}")
    for code in result.retired:
        print(f"  - {code}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
