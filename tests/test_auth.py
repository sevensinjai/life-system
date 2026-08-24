"""Registration, login, and token handling."""

from tests.conftest import REGISTRATION


def test_register_returns_a_token(client) -> None:
    response = client.post("/auth/register", json=REGISTRATION)

    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["expires_in"] > 0


def test_register_creates_a_level_one_player(auth_client) -> None:
    status = auth_client.get("/players/me").json()

    assert status["level"] == 1
    assert status["exp"] == 0
    assert status["name"] == "Sung Jinwoo"
    assert status["timezone"] == "Asia/Seoul"
    assert status["stats"] == {
        "strength": 10,
        "agility": 10,
        "vitality": 10,
        "intelligence": 10,
        "perception": 10,
    }


def test_duplicate_email_conflicts(client) -> None:
    client.post("/auth/register", json=REGISTRATION)
    response = client.post("/auth/register", json=REGISTRATION)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


def test_email_is_normalized_to_lowercase(client) -> None:
    client.post("/auth/register", json=REGISTRATION)
    response = client.post("/auth/register", json={**REGISTRATION, "email": "HUNTER@EXAMPLE.COM"})

    assert response.status_code == 409


def test_unknown_timezone_is_rejected(client) -> None:
    response = client.post(
        "/auth/register", json={**REGISTRATION, "timezone": "Middle/Earth"}
    )

    assert response.status_code == 422
    assert "IANA timezone" in response.json()["error"]["message"]


def test_short_password_is_rejected(client) -> None:
    response = client.post("/auth/register", json={**REGISTRATION, "password": "short"})

    assert response.status_code == 422


def test_login_succeeds_with_correct_credentials(client) -> None:
    client.post("/auth/register", json=REGISTRATION)
    response = client.post(
        "/auth/login",
        json={"email": REGISTRATION["email"], "password": REGISTRATION["password"]},
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_fails_with_wrong_password(client) -> None:
    client.post("/auth/register", json=REGISTRATION)
    response = client.post(
        "/auth/login", json={"email": REGISTRATION["email"], "password": "wrong-password"}
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthenticated"


def test_login_fails_identically_for_unknown_email(client) -> None:
    response = client.post(
        "/auth/login", json={"email": "nobody@example.com", "password": "whatever-1234"}
    )

    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Incorrect email or password."


def test_protected_route_requires_a_token(client) -> None:
    response = client.get("/players/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthenticated"


def test_garbage_token_is_rejected(client) -> None:
    response = client.get("/players/me", headers={"Authorization": "Bearer not-a-jwt"})

    assert response.status_code == 401


def test_token_signed_with_another_secret_is_rejected(client, settings) -> None:
    from app.config import Settings
    from app.security import create_access_token

    forged = create_access_token("1", Settings(environment="test", jwt_secret="a-different-secret-also-long-enough-x"))
    response = client.get("/players/me", headers={"Authorization": f"Bearer {forged}"})

    assert response.status_code == 401


def test_me_returns_the_account(auth_client) -> None:
    response = auth_client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == REGISTRATION["email"]
    assert "hashed_password" not in response.json()
