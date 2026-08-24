import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.errors import AppError, NotFoundError, register_error_handlers


class Payload(BaseModel):
    name: str


@pytest.fixture
def error_app() -> FastAPI:
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/missing")
    async def missing() -> None:
        raise NotFoundError("No cat with that id.")

    @app.get("/custom")
    async def custom() -> None:
        raise AppError("Something broke.", code="teapot")

    @app.post("/echo")
    async def echo(payload: Payload) -> Payload:
        return payload

    return app


@pytest.fixture
def error_client(error_app: FastAPI) -> TestClient:
    return TestClient(error_app, raise_server_exceptions=False)


def test_not_found_error_uses_envelope(error_client: TestClient) -> None:
    response = error_client.get("/missing")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "not_found", "message": "No cat with that id."}
    }


def test_app_error_defaults_to_500(error_client: TestClient) -> None:
    response = error_client.get("/custom")

    assert response.status_code == 500
    assert response.json() == {
        "error": {"code": "teapot", "message": "Something broke."}
    }


def test_unknown_route_uses_envelope(error_client: TestClient) -> None:
    response = error_client.get("/nope")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "http_error"


def test_request_validation_error_reports_details(error_client: TestClient) -> None:
    response = error_client.post("/echo", json={})

    assert response.status_code == 422
    body = response.json()["error"]
    assert body["code"] == "validation_error"
    assert body["details"][0]["loc"] == ["body", "name"]
