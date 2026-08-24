"""Written content: the pantheon, and the side quests it issues.

Everything a player reads that is not assembled from their own data lives
here, as plain data rather than as strings scattered through the services.
Two reasons. It is reviewable — a rewrite of a constellation's voice shows up
as a diff of what it says, not a diff of how the app works. And it is
swappable: adding another language later means another catalog beside this
one, not an audit of every f-string in the codebase.

Nothing here touches the database. `scripts/seed_pantheon.py` loads the
pantheon into it, and `services/broadcasting.py` reads the broadcast catalog
when it schedules one.
"""
