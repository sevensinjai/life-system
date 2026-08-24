"""The system event log and penalty history."""


def test_registering_and_questing_writes_events(auth_client) -> None:
    created = auth_client.post(
        "/quests", json={"title": "Run 10km", "difficulty": "S"}
    ).json()
    auth_client.post(f"/quests/{created['id']}/complete")

    types = [event["event_type"] for event in auth_client.get("/system/events").json()]

    assert "quest_created" in types
    assert "quest_completed" in types
    assert "level_up" in types


def test_events_are_newest_first(auth_client) -> None:
    for n in range(3):
        auth_client.post("/quests", json={"title": f"Quest {n}"})

    events = auth_client.get("/system/events").json()
    ids = [event["id"] for event in events]
    assert ids == sorted(ids, reverse=True)


def test_events_filter_by_type(auth_client) -> None:
    created = auth_client.post("/quests", json={"title": "Run"}).json()
    auth_client.post(f"/quests/{created['id']}/complete")

    events = auth_client.get("/system/events?event_type=quest_completed").json()

    assert len(events) == 1
    assert events[0]["event_type"] == "quest_completed"
    assert events[0]["payload"]["quest_id"] == created["id"]


def test_level_up_event_carries_its_payload(auth_client) -> None:
    created = auth_client.post(
        "/quests", json={"title": "Big one", "difficulty": "S"}
    ).json()
    auth_client.post(f"/quests/{created['id']}/complete")

    event = auth_client.get("/system/events?event_type=level_up").json()[0]

    assert event["payload"]["new_level"] == 4
    assert event["payload"]["levels_gained"] == 3
    assert event["payload"]["stat_points_gained"] == 9


def test_events_paginate(auth_client) -> None:
    for n in range(5):
        auth_client.post("/quests", json={"title": f"Quest {n}"})

    page = auth_client.get("/system/events?limit=2&offset=0").json()
    next_page = auth_client.get("/system/events?limit=2&offset=2").json()

    assert len(page) == 2
    assert len(next_page) == 2
    assert {e["id"] for e in page}.isdisjoint({e["id"] for e in next_page})


def test_penalty_history_starts_empty(auth_client) -> None:
    assert auth_client.get("/system/penalties").json() == []


def test_players_only_see_their_own_events(client, auth_client) -> None:
    auth_client.post("/quests", json={"title": "Mine"})

    other = client.post(
        "/auth/register",
        json={
            "email": "rival@example.com",
            "password": "cha-hae-in-1234",
            "name": "Rival",
            "timezone": "UTC",
        },
    ).json()

    events = client.get(
        "/system/events",
        headers={"Authorization": f"Bearer {other['access_token']}"},
    ).json()

    assert events == []
