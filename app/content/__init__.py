"""Written content: the pantheon, and the side quests it issues.

Everything a player reads that is not assembled from their own data lives
here, as plain data rather than as strings scattered through the services.
Two reasons. It is reviewable — a rewrite of a constellation's voice shows up
as a diff of what it says, not a diff of how the app works. And it is
swappable: adding another language later means another catalog beside this
one, not an audit of every f-string in the codebase.

Laid out by tradition, because the pantheon is large and grows:

    entries.py         the two shapes everything here takes
    pantheon/          who they are, and how each of them talks
    broadcasts/        the trials they issue
    challenges/        the audition each sets before it befriends anybody

A twenty-seventh constellation is an entry in `pantheon/<tradition>.py`, an
audition in `challenges/<tradition>.py`, and at least one trial in
`broadcasts/<tradition>.py`. No schema, no code — and the tests in
tests/test_constellations.py fail if any of the three is missing.

Nothing here touches the database. `scripts/seed_pantheon.py` loads the
pantheon into it, and `services/broadcasting.py` reads the broadcast catalog
when it schedules one.
"""
