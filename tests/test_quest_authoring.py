"""The authoring API: designing schedules and editing them afterward."""


def test_schedule_defaults_to_one_time(auth_client) -> None:
    quest = auth_client.post("/quests", json={"title": "Read a book"}).json()

    assert quest["schedule"]["kind"] == "once"
    assert quest["schedule"]["label"] == "One-time"
    assert quest["next_due_date"] is None
    assert quest["current_instance"]["period_end"] is None


def test_authoring_a_weekday_schedule(auth_client) -> None:
    quest = auth_client.post(
        "/quests",
        json={
            "title": "Gym",
            "schedule": {"kind": "weekdays", "days": [0, 2, 4]},
            "difficulty": "C",
        },
    ).json()

    assert quest["schedule"]["kind"] == "weekdays"
    assert quest["schedule"]["days"] == [0, 2, 4]
    assert quest["schedule"]["label"] == "Every Mon, Wed, Fri"


def test_authoring_an_interval_schedule(auth_client) -> None:
    quest = auth_client.post(
        "/quests",
        json={"title": "Deep clean", "schedule": {"kind": "interval", "interval_days": 3}},
    ).json()

    assert quest["schedule"]["label"] == "Every 3 days"
    assert quest["schedule"]["anchor"] is not None  # anchored at authoring time


def test_authoring_n_times_per_week(auth_client) -> None:
    """'Three runs a week' is a weekly quest whose target is three."""
    quest = auth_client.post(
        "/quests",
        json={
            "title": "Run",
            "schedule": {"kind": "weekly"},
            "target_count": 3,
            "unit": "runs",
            "difficulty": "B",
        },
    ).json()

    assert quest["schedule"]["label"] == "Every week (from Mon)"
    assert quest["current_instance"]["target_count"] == 3
    # A weekly period is open for seven days, not one.
    start = quest["current_instance"]["period_start"]
    end = quest["current_instance"]["period_end"]
    assert start < end


def test_logging_runs_across_the_week_clears_it(auth_client) -> None:
    quest = auth_client.post(
        "/quests",
        json={"title": "Run", "schedule": {"kind": "weekly"}, "target_count": 3},
    ).json()

    for _ in range(2):
        body = auth_client.post(f"/quests/{quest['id']}/progress", json={"amount": 1}).json()
        assert body["completed"] is False

    body = auth_client.post(f"/quests/{quest['id']}/progress", json={"amount": 1}).json()
    assert body["completed"] is True
    assert body["exp_gained"] == 50


def test_weekdays_without_days_is_rejected(auth_client) -> None:
    response = auth_client.post(
        "/quests", json={"title": "Gym", "schedule": {"kind": "weekdays"}}
    )

    assert response.status_code == 422
    assert "at least one day" in response.json()["error"]["message"]


def test_out_of_range_weekday_is_rejected(auth_client) -> None:
    response = auth_client.post(
        "/quests", json={"title": "Gym", "schedule": {"kind": "weekdays", "days": [0, 9]}}
    )

    assert response.status_code == 422


def test_interval_without_a_length_is_rejected(auth_client) -> None:
    response = auth_client.post(
        "/quests", json={"title": "Clean", "schedule": {"kind": "interval"}}
    )

    assert response.status_code == 422
    assert "interval_days" in response.json()["error"]["message"]


def test_mismatched_schedule_config_is_rejected(auth_client) -> None:
    """A daily schedule carrying weekdays is an authoring mistake worth catching."""
    response = auth_client.post(
        "/quests", json={"title": "X", "schedule": {"kind": "daily", "days": [0, 1]}}
    )

    assert response.status_code == 422
    assert "does not take specific weekdays" in response.json()["error"]["message"]


def test_duplicate_weekdays_are_normalized(auth_client) -> None:
    quest = auth_client.post(
        "/quests",
        json={"title": "Gym", "schedule": {"kind": "weekdays", "days": [4, 0, 4, 2]}},
    ).json()

    assert quest["schedule"]["days"] == [0, 2, 4]


def test_editing_the_schedule_keeps_the_original_anchor(auth_client) -> None:
    """Re-tuning an interval must not silently restart its cycle."""
    quest = auth_client.post(
        "/quests",
        json={"title": "Clean", "schedule": {"kind": "interval", "interval_days": 3}},
    ).json()
    anchor = quest["schedule"]["anchor"]

    updated = auth_client.patch(
        f"/quests/{quest['id']}",
        json={"schedule": {"kind": "interval", "interval_days": 5}},
    ).json()

    assert updated["schedule"]["interval_days"] == 5
    assert updated["schedule"]["anchor"] == anchor


def test_editing_the_schedule_can_move_the_anchor(auth_client) -> None:
    quest = auth_client.post(
        "/quests",
        json={"title": "Clean", "schedule": {"kind": "interval", "interval_days": 3}},
    ).json()

    updated = auth_client.patch(
        f"/quests/{quest['id']}",
        json={
            "schedule": {"kind": "interval", "interval_days": 3, "anchor": "2027-01-04"}
        },
    ).json()

    assert updated["schedule"]["anchor"] == "2027-01-04"


def test_switching_schedule_kind_clears_the_other_kinds_config(auth_client) -> None:
    quest = auth_client.post(
        "/quests",
        json={"title": "Gym", "schedule": {"kind": "weekdays", "days": [0, 2]}},
    ).json()

    updated = auth_client.patch(
        f"/quests/{quest['id']}", json={"schedule": {"kind": "daily"}}
    ).json()

    assert updated["schedule"]["kind"] == "daily"
    assert updated["schedule"]["days"] is None
    assert updated["schedule"]["interval_days"] is None


def test_editing_to_an_invalid_schedule_is_rejected(auth_client) -> None:
    quest = auth_client.post("/quests", json={"title": "Gym"}).json()

    response = auth_client.patch(
        f"/quests/{quest['id']}", json={"schedule": {"kind": "weekdays", "days": []}}
    )

    assert response.status_code == 422
    assert auth_client.get(f"/quests/{quest['id']}").json()["schedule"]["kind"] == "once"


def test_today_shows_everything_currently_open(auth_client) -> None:
    auth_client.post("/quests", json={"title": "Daily", "schedule": {"kind": "daily"}})
    auth_client.post("/quests", json={"title": "Weekly", "schedule": {"kind": "weekly"}})
    auth_client.post("/quests", json={"title": "One-time"})

    titles = {q["title"] for q in auth_client.get("/quests/today").json()}

    assert titles == {"Daily", "Weekly", "One-time"}


def test_today_omits_a_quest_not_due_now(auth_client, db) -> None:
    """A weekday quest authored off-schedule has no open period."""
    from datetime import timedelta

    from app.models import Player, Quest, QuestInstance

    auth_client.post(
        "/quests", json={"title": "Gym", "schedule": {"kind": "weekdays", "days": [0]}}
    )
    # Push the open instance into the past so nothing covers today.
    player = db.query(Player).one()
    for instance in db.query(QuestInstance).filter(
        QuestInstance.player_id == player.id
    ):
        instance.period_start = instance.period_start - timedelta(days=30)
        instance.period_end = instance.period_end - timedelta(days=30)
    db.commit()

    assert auth_client.get("/quests/today").json() == []


def test_progress_on_a_quest_with_no_open_period_explains_why(auth_client, db) -> None:
    from datetime import timedelta

    from app.models import Player, QuestInstance

    quest = auth_client.post(
        "/quests", json={"title": "Gym", "schedule": {"kind": "weekdays", "days": [0]}}
    ).json()

    player = db.query(Player).one()
    for instance in db.query(QuestInstance).filter(
        QuestInstance.player_id == player.id
    ):
        instance.period_start = instance.period_start - timedelta(days=30)
        instance.period_end = instance.period_end - timedelta(days=30)
    db.commit()

    response = auth_client.post(f"/quests/{quest['id']}/progress", json={"amount": 1})

    assert response.status_code == 422
    assert "no open period" in response.json()["error"]["message"]


def test_next_due_date_is_reported_for_recurring_quests(auth_client) -> None:
    quest = auth_client.post(
        "/quests", json={"title": "Daily", "schedule": {"kind": "daily"}}
    ).json()

    assert quest["next_due_date"] is not None
    assert quest["next_due_date"] > quest["current_instance"]["period_start"]
