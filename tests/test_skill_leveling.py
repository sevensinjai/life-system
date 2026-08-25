"""Skill EXP: practice, roll-up to parent skills, and quests that train one."""

import pytest

from app.config import Settings
from app.models import EventType, Skill
from app.services.skills import award_skill_exp, create_skill, get_skill


@pytest.fixture
def tuned() -> Settings:
    """Settings whose roll-up is halved, for the tests that check the dial."""
    return Settings(
        environment="test",
        jwt_secret="test-secret-that-is-long-enough-for-hs256",
        database_url="sqlite://",
        skill_exp_rollup=0.5,
    )


def add(auth_client, name: str, parent_id: int | None = None) -> dict:
    response = auth_client.post("/skills", json={"name": name, "parent_id": parent_id})
    assert response.status_code == 201, response.text
    return response.json()


def branch(auth_client) -> tuple[dict, dict, dict]:
    """Singing -> Pitch accuracy -> Interval jumps."""
    singing = add(auth_client, "Singing")
    pitch = add(auth_client, "Pitch accuracy", singing["id"])
    jumps = add(auth_client, "Interval jumps", pitch["id"])
    return singing, pitch, jumps


def test_practice_credits_the_skill_and_everything_above_it(auth_client) -> None:
    singing, pitch, jumps = branch(auth_client)

    body = auth_client.post(f"/skills/{jumps['id']}/practice", json={"minutes": 60}).json()

    assert [award["name"] for award in body["awards"]] == [
        "Interval jumps",
        "Pitch accuracy",
        "Singing",
    ]
    assert [award["exp_gained"] for award in body["awards"]] == [60, 60, 60]
    assert [award["distance"] for award in body["awards"]] == [0, 1, 2]


def test_a_top_level_skill_credits_only_itself(auth_client) -> None:
    guitar = add(auth_client, "Guitar")

    body = auth_client.post(f"/skills/{guitar['id']}/practice", json={"exp": 40}).json()

    assert len(body["awards"]) == 1
    assert body["skill"]["exp"] == 40
    assert body["skill"]["exp_to_next_level"] == 100
    assert body["skill"]["exp_progress"] == 0.4


def test_enough_practice_levels_a_skill_up(auth_client) -> None:
    """Level 1 -> 2 costs 100 on the default curve."""
    guitar = add(auth_client, "Guitar")

    auth_client.post(f"/skills/{guitar['id']}/practice", json={"exp": 60})
    body = auth_client.post(f"/skills/{guitar['id']}/practice", json={"exp": 60}).json()

    assert body["skill"]["level"] == 2
    assert body["skill"]["exp"] == 20  # 120 earned, 100 spent on the level
    assert body["awards"][0]["leveled_up"] is True
    assert body["skill"]["total_exp_earned"] == 120


def test_a_parent_levels_off_its_children(auth_client) -> None:
    """The point of the graph: Singing advances because its sub-skills do."""
    singing, _, jumps = branch(auth_client)

    auth_client.post(f"/skills/{jumps['id']}/practice", json={"exp": 100})

    assert auth_client.get(f"/skills/{singing['id']}").json()["level"] == 2


def test_a_level_up_reaches_the_system_log(auth_client) -> None:
    guitar = add(auth_client, "Guitar")

    auth_client.post(f"/skills/{guitar['id']}/practice", json={"exp": 150})

    events = auth_client.get("/system/events?event_type=skill_level_up").json()
    assert len(events) == 1
    assert events[0]["payload"]["new_level"] == 2
    assert events[0]["payload"]["skill_id"] == guitar["id"]


def test_practice_must_be_positive(auth_client) -> None:
    guitar = add(auth_client, "Guitar")

    assert (
        auth_client.post(f"/skills/{guitar['id']}/practice", json={"exp": 0}).status_code
        == 422
    )
    assert (
        auth_client.post(
            f"/skills/{guitar['id']}/practice", json={"exp": -5}
        ).status_code
        == 422
    )


def test_an_archived_skill_takes_no_practice(auth_client) -> None:
    guitar = add(auth_client, "Guitar")
    auth_client.delete(f"/skills/{guitar['id']}")

    response = auth_client.post(f"/skills/{guitar['id']}/practice", json={"exp": 50})

    assert response.status_code == 422
    assert "archived" in response.json()["error"]["message"]


def test_the_rollup_rate_is_a_setting(auth_client, db, player, tuned) -> None:
    """At 0.5 the parent takes half and the grandparent a quarter."""
    singing = create_skill(db, player, tuned, name="Singing")
    pitch = create_skill(db, player, tuned, name="Pitch", parent_id=singing.id)
    jumps = create_skill(db, player, tuned, name="Jumps", parent_id=pitch.id)
    db.commit()

    awards = award_skill_exp(db, player, jumps, 100, tuned)
    db.commit()

    assert [award.exp_gained for award in awards] == [100, 50, 25]
    assert get_skill(db, player, singing.id).exp == 25


# --------------------------------------------------------------------------
# Quests that train a skill
# --------------------------------------------------------------------------


def author(auth_client, **overrides) -> dict:
    payload = {"title": "Practise scales", "difficulty": "C"} | overrides
    response = auth_client.post("/quests", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_a_quest_can_name_a_skill(auth_client) -> None:
    _, pitch, _ = branch(auth_client)

    quest = author(auth_client, skill_id=pitch["id"])

    assert quest["skill_id"] == pitch["id"]
    # A C-rank quest is worth 200 EXP, and the skill inherits that by default.
    assert quest["skill_exp_reward"] == 200


def test_the_skill_reward_cannot_be_set_apart_from_practice_minutes(auth_client) -> None:
    _, pitch, _ = branch(auth_client)

    response = auth_client.post(
        "/quests",
        json={
            "title": "Practise scales",
            "practice_minutes": 20,
            "skill_id": pitch["id"],
            "skill_exp_reward": 25,
        },
    )

    assert response.status_code == 422
    assert "must equal practice_minutes" in response.json()["error"]["message"]


def test_clearing_a_quest_trains_its_skill_and_the_branch_above(auth_client) -> None:
    singing, pitch, _ = branch(auth_client)
    quest = author(auth_client, skill_id=pitch["id"], practice_minutes=120)

    body = auth_client.post(f"/quests/{quest['id']}/complete").json()

    assert [award["name"] for award in body["skill_awards"]] == [
        "Pitch accuracy",
        "Singing",
    ]
    assert body["exp_gained"] == 120
    assert auth_client.get(f"/skills/{singing['id']}").json()["level"] == 2


def test_progress_that_clears_a_quest_pays_the_skill_too(auth_client) -> None:
    _, pitch, _ = branch(auth_client)
    quest = author(
        auth_client, skill_id=pitch["id"], target_count=3, unit="sets",
        practice_minutes=30,
    )

    partial = auth_client.post(f"/quests/{quest['id']}/progress", json={"amount": 2})
    assert partial.json()["skill_awards"] == []  # nothing until it clears

    cleared = auth_client.post(f"/quests/{quest['id']}/progress", json={"amount": 1})
    assert cleared.json()["completed"] is True
    assert cleared.json()["skill_awards"][0]["exp_gained"] == 30


def test_a_quest_that_names_no_skill_pays_no_skill(auth_client) -> None:
    quest = author(auth_client)

    body = auth_client.post(f"/quests/{quest['id']}/complete").json()

    assert body["skill_awards"] == []
    assert body["exp_gained"] == 200


def test_a_quest_cannot_point_at_someone_elses_skill(auth_client, client) -> None:
    mine = add(auth_client, "Singing")

    other = client.post(
        "/auth/register",
        json={
            "email": "other@example.com",
            "password": "another-hunter-1",
            "name": "Cha Hae-In",
            "timezone": "Asia/Seoul",
        },
    ).json()

    response = client.post(
        "/quests",
        json={"title": "Steal", "skill_id": mine["id"]},
        headers={"Authorization": f"Bearer {other['access_token']}"},
    )

    assert response.status_code == 404


def test_a_quest_can_be_relinked_to_another_skill(auth_client) -> None:
    singing = add(auth_client, "Singing")
    guitar = add(auth_client, "Guitar")
    quest = author(auth_client, skill_id=singing["id"], practice_minutes=40)

    edited = auth_client.patch(
        f"/quests/{quest['id']}", json={"skill_id": guitar["id"]}
    ).json()

    assert edited["skill_id"] == guitar["id"]
    assert edited["skill_exp_reward"] == 40

    auth_client.post(f"/quests/{quest['id']}/complete")
    assert auth_client.get(f"/skills/{guitar['id']}").json()["exp"] == 40
    assert auth_client.get(f"/skills/{singing['id']}").json()["exp"] == 0


def test_a_quest_whose_skill_was_archived_still_completes(auth_client) -> None:
    """Clearing the quest stays valid; it just trains nothing."""
    singing = add(auth_client, "Singing")
    quest = author(auth_client, skill_id=singing["id"])
    auth_client.delete(f"/skills/{singing['id']}")

    body = auth_client.post(f"/quests/{quest['id']}/complete")

    assert body.status_code == 200
    assert body.json()["skill_awards"] == []
    assert body.json()["exp_gained"] == 200


def test_deleting_a_skill_row_leaves_its_quests_alone(auth_client, db, player) -> None:
    """The FK is SET NULL: losing a skill must not take the quest with it."""
    singing = add(auth_client, "Singing")
    quest = author(auth_client, skill_id=singing["id"])

    db.delete(db.get(Skill, singing["id"]))
    db.commit()

    still_there = auth_client.get(f"/quests/{quest['id']}")
    assert still_there.status_code == 200
    assert still_there.json()["skill_id"] is None


def test_skill_events_are_logged_when_a_skill_is_created(auth_client) -> None:
    add(auth_client, "Singing")

    events = auth_client.get(
        f"/system/events?event_type={EventType.SKILL_CREATED.value}"
    ).json()

    assert len(events) == 1
    assert "Singing" in events[0]["message"]
