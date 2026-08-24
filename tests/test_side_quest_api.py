"""The side quest API: the opt-in switch, and answering what it lets through."""

from datetime import UTC, datetime, timedelta

import pytest

from app.models import QuestDifficulty
from app.services import side_quests

NOW = datetime(2026, 8, 24, 12, tzinfo=UTC)


@pytest.fixture
def broadcast(db, auth_client):
    """A side quest already out in the world, waiting for opted-in players.

    Broadcast before anyone opts in, so the catch-up path is what delivers it —
    which is the path a real late opt-in takes.
    """
    side_quest = side_quests.create_side_quest(
        db,
        title="Slay ten shadows",
        herald="The Constellation of the Fallen Star",
        difficulty=QuestDifficulty.C,
        target_count=10,
        unit="shadows",
        penalty_exp=50,
        expires_at=NOW + timedelta(days=30),
        now=NOW,
    )
    side_quests.broadcast(db, side_quest, now=NOW)
    db.commit()
    return side_quest


def opt_in(auth_client, **fields) -> dict:
    fields.setdefault("is_opted_in", True)
    response = auth_client.patch("/side-quests/preferences", json=fields)
    assert response.status_code == 200, response.text
    return response.json()


# --------------------------------------------------------------------------
# The switch
# --------------------------------------------------------------------------


def test_a_new_player_reads_back_as_opted_out(auth_client) -> None:
    body = auth_client.get("/side-quests/preferences").json()

    assert body["is_opted_in"] is False
    assert body["opted_in_at"] is None
    assert body["open_offers"] == 0


def test_the_default_frequency_is_occasional(auth_client) -> None:
    body = auth_client.get("/side-quests/preferences").json()

    assert body["frequency"] == "occasional"
    assert body["offers_per_week"] == 3


def test_opting_in_delivers_what_is_already_open(auth_client, broadcast) -> None:
    """Saying yes has an effect now, not at the next broadcast."""
    body = opt_in(auth_client)

    assert body["is_opted_in"] is True
    assert body["open_offers"] == 1

    offers = auth_client.get("/side-quests").json()
    assert offers[0]["side_quest"]["title"] == "Slay ten shadows"
    assert offers[0]["status"] == "offered"


def test_staying_opted_out_delivers_nothing(auth_client, broadcast) -> None:
    assert auth_client.get("/side-quests").json() == []


def test_a_rank_cap_keeps_harder_broadcasts_out(auth_client, broadcast) -> None:
    opt_in(auth_client, max_difficulty="E")

    assert auth_client.get("/side-quests").json() == []


def test_the_rank_cap_can_be_lifted_with_null(auth_client, broadcast) -> None:
    opt_in(auth_client, max_difficulty="E")
    body = opt_in(auth_client, max_difficulty=None)

    assert body["max_difficulty"] is None
    assert len(auth_client.get("/side-quests").json()) == 1


def test_an_untouched_field_is_left_alone(auth_client) -> None:
    opt_in(auth_client, frequency="rare")
    body = auth_client.patch(
        "/side-quests/preferences", json={"auto_accept": True}
    ).json()

    assert body["frequency"] == "rare"
    assert body["auto_accept"] is True
    assert body["is_opted_in"] is True


def test_opting_out_stops_new_offers_but_keeps_what_was_accepted(
    auth_client, broadcast, db
) -> None:
    opt_in(auth_client)
    offer_id = auth_client.get("/side-quests").json()[0]["id"]
    auth_client.post(f"/side-quests/{offer_id}/accept")

    body = auth_client.patch(
        "/side-quests/preferences", json={"is_opted_in": False}
    ).json()

    assert body["is_opted_in"] is False
    assert body["open_offers"] == 1
    assert auth_client.get(f"/side-quests/{offer_id}").json()["status"] == "accepted"


def test_the_response_reports_the_week_so_far(auth_client, broadcast) -> None:
    body = opt_in(auth_client)

    assert body["offers_this_week"] == 1
    assert body["offers_per_week"] == 3


# --------------------------------------------------------------------------
# Answering
# --------------------------------------------------------------------------


def test_accepting_then_logging_progress_clears_it(auth_client, broadcast) -> None:
    opt_in(auth_client)
    offer_id = auth_client.get("/side-quests").json()[0]["id"]

    auth_client.post(f"/side-quests/{offer_id}/accept")
    response = auth_client.post(
        f"/side-quests/{offer_id}/progress", json={"amount": 10}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["completed"] is True
    assert body["offer"]["status"] == "completed"
    assert auth_client.get("/players/me").json()["total_exp_earned"] == 200


def test_declining_is_free_and_final(auth_client, broadcast) -> None:
    opt_in(auth_client)
    offer_id = auth_client.get("/side-quests").json()[0]["id"]

    assert auth_client.post(f"/side-quests/{offer_id}/decline").json()["status"] == (
        "declined"
    )

    again = auth_client.post(f"/side-quests/{offer_id}/accept")
    assert again.status_code == 422
    assert auth_client.get("/players/me").json()["exp"] == 0


def test_progress_without_accepting_is_refused(auth_client, broadcast) -> None:
    opt_in(auth_client)
    offer_id = auth_client.get("/side-quests").json()[0]["id"]

    response = auth_client.post(
        f"/side-quests/{offer_id}/progress", json={"amount": 1}
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_another_players_offer_is_not_yours(auth_client, client, broadcast) -> None:
    opt_in(auth_client)
    offer_id = auth_client.get("/side-quests").json()[0]["id"]

    other = client.post(
        "/auth/register",
        json={
            "email": "someone@example.com",
            "password": "another-hunter-1",
            "name": "Cha Hae-In",
            "timezone": "Asia/Seoul",
        },
    ).json()["access_token"]

    response = auth_client.get(
        f"/side-quests/{offer_id}", headers={"Authorization": f"Bearer {other}"}
    )
    assert response.status_code == 404


def test_offers_can_be_filtered_by_status(auth_client, broadcast) -> None:
    opt_in(auth_client)
    offer_id = auth_client.get("/side-quests").json()[0]["id"]
    auth_client.post(f"/side-quests/{offer_id}/decline")

    assert auth_client.get("/side-quests?status=declined").json() != []
    assert auth_client.get("/side-quests?live_only=true").json() == []


def test_auto_accept_arrives_already_accepted(auth_client, broadcast) -> None:
    opt_in(auth_client, auto_accept=True)

    assert auth_client.get("/side-quests").json()[0]["status"] == "accepted"


def test_deadlines_come_back_with_a_timezone(auth_client, broadcast) -> None:
    """A client that reads a UTC deadline as local time is wrong by hours."""
    opt_in(auth_client)

    expires_at = auth_client.get("/side-quests").json()[0]["expires_at"]
    assert expires_at.endswith("Z") or "+00:00" in expires_at
