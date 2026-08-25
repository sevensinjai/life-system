"""Quest creation, progress tracking, completion, and rewards."""

import pytest

PUSHUPS = {
    "title": "100 push-ups",
    "schedule": {"kind": "daily"},
    "difficulty": "D",
    "target_count": 100,
    "unit": "reps",
    "practice_minutes": 10,
    "stat_reward": "strength",
    "stat_reward_amount": 1,
}


@pytest.fixture
def quest(auth_client):
    response = auth_client.post("/quests", json=PUSHUPS)
    assert response.status_code == 201, response.text
    return response.json()


def test_create_quest_opens_an_instance_for_today(quest) -> None:
    assert quest["title"] == "100 push-ups"
    assert quest["practice_minutes"] == 10
    assert quest["exp_reward"] == 10  # deprecated compatibility mirror
    assert quest["current_instance"]["practice_minutes"] == 10
    assert quest["current_instance"]["progress"] == 0
    assert quest["current_instance"]["target_count"] == 100
    assert quest["current_instance"]["status"] == "active"


def test_difficulty_sets_the_default_exp_reward(auth_client) -> None:
    rewards = {}
    for difficulty in ("E", "D", "C", "B", "A", "S"):
        response = auth_client.post(
            "/quests", json={"title": f"{difficulty} quest", "difficulty": difficulty}
        )
        rewards[difficulty] = response.json()["exp_reward"]

    assert rewards == {"E": 50, "D": 100, "C": 200, "B": 400, "A": 800, "S": 1600}


def test_practice_minutes_are_the_completion_exp(auth_client) -> None:
    response = auth_client.post(
        "/quests", json={"title": "Custom", "difficulty": "S", "practice_minutes": 5}
    )
    assert response.json()["practice_minutes"] == 5
    assert response.json()["exp_reward"] == 5


def test_count_and_pace_convert_to_completion_minutes(auth_client) -> None:
    response = auth_client.post(
        "/quests",
        json={
            "title": "100 push-ups",
            "target_count": 100,
            "unit": "reps",
            "units_per_minute": 10,
        },
    )

    quest = response.json()
    assert response.status_code == 201
    assert quest["practice_minutes"] == 10
    assert quest["current_instance"]["practice_minutes"] == 10


def test_conversion_rounds_partial_minutes_up(auth_client) -> None:
    quest = auth_client.post(
        "/quests",
        json={"title": "Read", "target_count": 21, "units_per_minute": 2},
    ).json()

    assert quest["practice_minutes"] == 11


def test_partial_progress_does_not_complete(auth_client, quest) -> None:
    response = auth_client.post(f"/quests/{quest['id']}/progress", json={"amount": 40})

    body = response.json()
    assert response.status_code == 200
    assert body["completed"] is False
    assert body["instance"]["progress"] == 40
    assert body["exp_gained"] == 0


def test_reaching_the_target_completes_and_pays_out(auth_client, quest) -> None:
    auth_client.post(f"/quests/{quest['id']}/progress", json={"amount": 60})
    response = auth_client.post(f"/quests/{quest['id']}/progress", json={"amount": 40})

    body = response.json()
    assert body["completed"] is True
    assert body["instance"]["status"] == "completed"
    assert body["instance"]["completed_at"] is not None
    assert body["exp_gained"] == 10
    assert body["leveled_up"] is False


def test_completion_grants_the_stat_reward(auth_client, quest) -> None:
    auth_client.post(f"/quests/{quest['id']}/progress", json={"amount": 100})

    status = auth_client.get("/players/me").json()
    assert status["stats"]["strength"] == 11


def test_overshooting_the_target_still_completes_once(auth_client, quest) -> None:
    response = auth_client.post(f"/quests/{quest['id']}/progress", json={"amount": 500})

    assert response.json()["completed"] is True
    assert response.json()["instance"]["progress"] == 500


def test_progress_on_a_completed_instance_is_rejected(auth_client, quest) -> None:
    auth_client.post(f"/quests/{quest['id']}/progress", json={"amount": 100})
    response = auth_client.post(f"/quests/{quest['id']}/progress", json={"amount": 1})

    assert response.status_code == 422
    assert "already completed" in response.json()["error"]["message"]


def test_zero_progress_is_rejected(auth_client, quest) -> None:
    response = auth_client.post(f"/quests/{quest['id']}/progress", json={"amount": 0})

    assert response.status_code == 422


def test_negative_progress_corrects_an_overcount(auth_client, quest) -> None:
    auth_client.post(f"/quests/{quest['id']}/progress", json={"amount": 50})
    response = auth_client.post(f"/quests/{quest['id']}/progress", json={"amount": -20})

    assert response.json()["instance"]["progress"] == 30


def test_progress_cannot_go_below_zero(auth_client, quest) -> None:
    response = auth_client.post(f"/quests/{quest['id']}/progress", json={"amount": -50})

    assert response.json()["instance"]["progress"] == 0


def test_complete_endpoint_clears_regardless_of_progress(auth_client, quest) -> None:
    response = auth_client.post(f"/quests/{quest['id']}/complete")

    body = response.json()
    assert body["completed"] is True
    assert body["instance"]["progress"] == 100  # snapped up to the target
    assert body["exp_gained"] == 10


def test_completing_twice_is_rejected(auth_client, quest) -> None:
    auth_client.post(f"/quests/{quest['id']}/complete")
    response = auth_client.post(f"/quests/{quest['id']}/complete")

    assert response.status_code == 422


def test_clearing_a_one_time_quest_archives_it(auth_client) -> None:
    created = auth_client.post(
        "/quests", json={"title": "Read a book", "schedule": {"kind": "once"}}
    ).json()

    response = auth_client.post(f"/quests/{created['id']}/complete")

    assert response.json()["quest"]["is_active"] is False


def test_clearing_a_recurring_quest_leaves_it_active(auth_client, quest) -> None:
    response = auth_client.post(f"/quests/{quest['id']}/complete")

    assert response.json()["quest"]["is_active"] is True


def test_listing_excludes_archived_by_default(auth_client, quest) -> None:
    auth_client.delete(f"/quests/{quest['id']}")

    assert auth_client.get("/quests").json() == []
    assert len(auth_client.get("/quests?include_archived=true").json()) == 1


def test_listing_filters_by_schedule(auth_client, quest) -> None:
    auth_client.post("/quests", json={"title": "One-off", "schedule": {"kind": "once"}})

    assert len(auth_client.get("/quests?schedule=daily").json()) == 1
    assert len(auth_client.get("/quests?schedule=once").json()) == 1
    assert len(auth_client.get("/quests?recurring_only=true").json()) == 1
    assert len(auth_client.get("/quests").json()) == 2


def test_editing_target_count_updates_the_open_instance(auth_client, quest) -> None:
    response = auth_client.patch(f"/quests/{quest['id']}", json={"target_count": 50})

    assert response.json()["target_count"] == 50
    assert response.json()["current_instance"]["target_count"] == 50


def test_archive_preserves_history(auth_client, quest) -> None:
    auth_client.post(f"/quests/{quest['id']}/progress", json={"amount": 100})
    auth_client.delete(f"/quests/{quest['id']}")

    archived = auth_client.get(f"/quests/{quest['id']}").json()
    assert archived["is_active"] is False
    assert archived["current_instance"]["status"] == "completed"


def test_unknown_quest_is_a_404(auth_client) -> None:
    response = auth_client.get("/quests/9999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_players_cannot_reach_each_others_quests(client, auth_client, quest) -> None:
    other = client.post(
        "/auth/register",
        json={
            "email": "rival@example.com",
            "password": "cha-hae-in-1234",
            "name": "Rival",
            "timezone": "UTC",
        },
    ).json()

    response = client.get(
        f"/quests/{quest['id']}",
        headers={"Authorization": f"Bearer {other['access_token']}"},
    )
    assert response.status_code == 404
