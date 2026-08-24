"""The status window, stat allocation, and profile updates."""

import pytest


@pytest.fixture
def leveled_client(auth_client):
    """A player with stat points banked, by clearing an S-rank quest."""
    created = auth_client.post(
        "/quests", json={"title": "Clear a dungeon", "difficulty": "S"}
    ).json()
    auth_client.post(f"/quests/{created['id']}/complete")
    return auth_client


def test_status_reports_progress_toward_the_next_level(auth_client) -> None:
    created = auth_client.post(
        "/quests", json={"title": "Study", "difficulty": "E"}
    ).json()
    auth_client.post(f"/quests/{created['id']}/complete")  # 50 EXP, no level up

    status = auth_client.get("/players/me").json()
    assert status["level"] == 1
    assert status["exp"] == 50
    assert status["exp_to_next_level"] == 100
    assert status["exp_progress"] == 0.5


def test_total_exp_earned_ignores_penalties(auth_client) -> None:
    created = auth_client.post(
        "/quests", json={"title": "Study", "difficulty": "C"}
    ).json()
    auth_client.post(f"/quests/{created['id']}/complete")

    assert auth_client.get("/players/me").json()["total_exp_earned"] == 200


def test_level_ups_grant_stat_points(leveled_client) -> None:
    status = leveled_client.get("/players/me").json()

    # 1600 EXP carries the player from level 1 to level 4: three levels, nine points.
    assert status["level"] == 4
    assert status["stat_points"] == 9


def test_allocating_points_raises_stats(leveled_client) -> None:
    response = leveled_client.post(
        "/players/me/allocate", json={"strength": 5, "vitality": 2}
    )

    body = response.json()
    assert body["stats"]["strength"] == 15
    assert body["stats"]["vitality"] == 12
    assert body["stat_points"] == 2


def test_overspending_is_rejected_wholesale(leveled_client) -> None:
    response = leveled_client.post("/players/me/allocate", json={"strength": 100})

    assert response.status_code == 422
    assert "Not enough stat points" in response.json()["error"]["message"]
    # Nothing was applied.
    assert leveled_client.get("/players/me").json()["stats"]["strength"] == 10


def test_allocating_nothing_is_rejected(leveled_client) -> None:
    response = leveled_client.post("/players/me/allocate", json={})

    assert response.status_code == 422


def test_negative_allocation_is_rejected(leveled_client) -> None:
    response = leveled_client.post("/players/me/allocate", json={"strength": -5})

    assert response.status_code == 422


def test_update_name_and_timezone(auth_client) -> None:
    response = auth_client.patch(
        "/players/me", json={"name": "Shadow Monarch", "timezone": "America/New_York"}
    )

    body = response.json()
    assert body["name"] == "Shadow Monarch"
    assert body["timezone"] == "America/New_York"


def test_update_rejects_unknown_timezone(auth_client) -> None:
    response = auth_client.patch("/players/me", json={"timezone": "Mars/Olympus"})

    assert response.status_code == 422
    assert auth_client.get("/players/me").json()["timezone"] == "Asia/Seoul"
