"""The quote collection API, and the daily quote a lock screen renders."""

from datetime import date, timedelta

from app.services.quotes import pick_for_day, quote_of_the_day, rotation_ids


def write(auth_client, text: str, author: str | None = None) -> dict:
    response = auth_client.post("/quotes", json={"text": text, "author": author})
    assert response.status_code == 201, response.text
    return response.json()


def test_writing_a_quote(auth_client) -> None:
    quote = write(auth_client, "Arise.", "The System")

    assert quote["text"] == "Arise."
    assert quote["author"] == "The System"
    assert quote["is_active"] is True


def test_a_quote_needs_text(auth_client) -> None:
    response = auth_client.post("/quotes", json={"text": "   "})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_pasted_whitespace_is_collapsed(auth_client) -> None:
    quote = write(auth_client, "Keep\n  going.\t")

    assert quote["text"] == "Keep going."


def test_a_blank_author_is_stored_as_none(auth_client) -> None:
    assert write(auth_client, "Something I wrote.", "  ")["author"] is None


def test_writing_a_batch(auth_client) -> None:
    response = auth_client.post(
        "/quotes/bulk",
        json={
            "quotes": [
                {"text": "Arise.", "author": "The System"},
                {"text": "Hard days make hard people."},
                {"text": "One more rep."},
            ]
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["created_count"] == 3
    assert body["skipped_count"] == 0
    assert len(auth_client.get("/quotes").json()) == 3


def test_a_batch_skips_quotes_already_in_rotation(auth_client) -> None:
    """Re-importing a partly-entered list adds only what is new."""
    write(auth_client, "Arise.")

    body = auth_client.post(
        "/quotes/bulk",
        json={
            "quotes": [
                {"text": "arise.", "author": "someone else"},  # same words
                {"text": "  Arise. "},  # same again, once collapsed
                {"text": "One more rep."},
            ]
        },
    ).json()

    assert body["created_count"] == 1
    assert body["skipped_count"] == 2
    assert body["created"][0]["text"] == "One more rep."
    assert len(auth_client.get("/quotes").json()) == 2


def test_an_empty_batch_is_rejected(auth_client) -> None:
    response = auth_client.post("/quotes/bulk", json={"quotes": []})

    assert response.status_code == 422


def test_todays_quote_is_one_of_yours(auth_client) -> None:
    for text in ("Arise.", "One more rep.", "Hard days make hard people."):
        write(auth_client, text)

    body = auth_client.get("/quotes/today").json()

    assert body["pool_size"] == 3
    assert body["quote"]["text"] in {
        "Arise.",
        "One more rep.",
        "Hard days make hard people.",
    }
    assert body["local_date"]
    assert body["refresh_after"]


def test_todays_quote_does_not_change_when_asked_again(auth_client) -> None:
    """The widget polls; it must not flicker between quotes within a day."""
    for text in ("Arise.", "One more rep.", "Keep going."):
        write(auth_client, text)

    picks = {auth_client.get("/quotes/today").json()["quote"]["id"] for _ in range(10)}

    assert len(picks) == 1


def test_an_empty_collection_returns_no_quote_rather_than_an_error(auth_client) -> None:
    """A widget with nothing to show should render a prompt, not a 404."""
    body = auth_client.get("/quotes/today").json()

    assert body["quote"] is None
    assert body["pool_size"] == 0
    assert body["refresh_after"]


def test_tomorrow_moves_on_to_another_quote(auth_client, db, player) -> None:
    for text in ("Arise.", "One more rep.", "Keep going."):
        write(auth_client, text)

    today = date(2026, 8, 24)
    picked_today, _ = quote_of_the_day(db, player, today)
    picked_tomorrow, _ = quote_of_the_day(db, player, today + timedelta(days=1))

    assert picked_today.id != picked_tomorrow.id


def test_archiving_drops_a_quote_out_of_the_rotation(auth_client, db, player) -> None:
    kept = write(auth_client, "Arise.")
    retired = write(auth_client, "Something I no longer believe.")

    response = auth_client.delete(f"/quotes/{retired['id']}")

    assert response.status_code == 200
    assert response.json()["is_active"] is False
    assert rotation_ids(db, player) == [kept["id"]]
    assert [q["id"] for q in auth_client.get("/quotes").json()] == [kept["id"]]


def test_an_archived_quote_still_resolves_by_id(auth_client) -> None:
    """A widget still holding yesterday's id should render it, not error."""
    quote = write(auth_client, "Arise.")
    auth_client.delete(f"/quotes/{quote['id']}")

    response = auth_client.get(f"/quotes/{quote['id']}")

    assert response.status_code == 200
    assert response.json()["text"] == "Arise."


def test_archived_quotes_can_be_listed_and_restored(auth_client) -> None:
    quote = write(auth_client, "Arise.")
    auth_client.delete(f"/quotes/{quote['id']}")

    assert auth_client.get("/quotes").json() == []
    assert len(auth_client.get("/quotes?include_archived=true").json()) == 1

    restored = auth_client.patch(f"/quotes/{quote['id']}", json={"is_active": True})

    assert restored.json()["is_active"] is True
    assert len(auth_client.get("/quotes").json()) == 1


def test_editing_a_quote(auth_client) -> None:
    quote = write(auth_client, "Arise.", "The System")

    edited = auth_client.patch(
        f"/quotes/{quote['id']}", json={"text": "  Arise,  hunter. "}
    ).json()

    assert edited["text"] == "Arise, hunter."
    assert edited["author"] == "The System"  # untouched fields are left alone


def test_an_edit_can_clear_the_author(auth_client) -> None:
    quote = write(auth_client, "Arise.", "The System")

    edited = auth_client.patch(f"/quotes/{quote['id']}", json={"author": None}).json()

    assert edited["author"] is None


def test_a_missing_quote_is_a_404(auth_client) -> None:
    response = auth_client.get("/quotes/9999")

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"
    assert body["error"]["message"] == "No quote with id 9999."


def test_quotes_are_private_to_their_author(auth_client, client) -> None:
    """One player's collection must never surface in another's rotation."""
    mine = write(auth_client, "Arise.")

    other = client.post(
        "/auth/register",
        json={
            "email": "other@example.com",
            "password": "another-hunter-1",
            "name": "Cha Hae-In",
            "timezone": "Asia/Seoul",
        },
    ).json()
    headers = {"Authorization": f"Bearer {other['access_token']}"}

    assert client.get("/quotes", headers=headers).json() == []
    assert client.get("/quotes/today", headers=headers).json()["quote"] is None
    assert client.get(f"/quotes/{mine['id']}", headers=headers).status_code == 404


def test_quotes_require_authentication(client) -> None:
    assert client.get("/quotes/today").status_code == 401
    assert client.post("/quotes", json={"text": "Arise."}).status_code == 401


def test_the_rotation_covers_the_whole_collection_over_time(
    auth_client, db, player
) -> None:
    """Across as many days as there are quotes, every one gets a turn."""
    for n in range(5):
        write(auth_client, f"Quote number {n}.")

    ids = rotation_ids(db, player)
    start = date(2026, 8, 24)
    seen = {pick_for_day(ids, start + timedelta(days=n)) for n in range(len(ids))}

    assert seen == set(ids)
