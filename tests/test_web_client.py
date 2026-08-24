"""The browser client mounted alongside the API."""

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import WEB_CLIENT_DIR, create_app

STATIC = WEB_CLIENT_DIR / "static"


def test_index_is_served(client: TestClient) -> None:
    response = client.get("/web/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "SYSTEM" in response.text


def test_root_redirects_to_the_client(client: TestClient) -> None:
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/web/"


def test_client_assets_are_served(client: TestClient) -> None:
    for path in ("/web/static/styles.css", "/web/static/app.js", "/web/static/api.js"):
        assert client.get(path).status_code == 200, path


@pytest.mark.parametrize(
    "asset",
    sorted(str(path.relative_to(WEB_CLIENT_DIR)) for path in STATIC.rglob("*.js")),
)
def test_every_module_import_resolves(asset: str) -> None:
    """Imports are relative paths the browser fetches, so a typo is a 404."""
    source = (WEB_CLIENT_DIR / asset).read_text()
    for target in re.findall(r"""from ["'](\.[^"']+)["']""", source):
        resolved = (WEB_CLIENT_DIR / asset).parent / target
        assert resolved.is_file(), f"{asset} imports missing {target}"


def test_index_references_existing_assets() -> None:
    index = (WEB_CLIENT_DIR / "index.html").read_text()
    for reference in re.findall(r"""(?:href|src)=["']\./([^"']+)["']""", index):
        assert (WEB_CLIENT_DIR / reference).is_file(), reference


def test_client_can_be_disabled(session_factory) -> None:
    """An app-only deployment turns the whole thing off."""
    settings = Settings(
        environment="test",
        jwt_secret="test-secret-that-is-long-enough-for-hs256",
        database_url="sqlite://",
        web_client=False,
    )
    app = create_app(settings)

    with TestClient(app, raise_server_exceptions=False) as disabled:
        assert disabled.get("/web/").status_code == 404
        assert disabled.get("/", follow_redirects=False).status_code == 404
        assert disabled.get("/health").status_code == 200


def test_client_lives_inside_the_package() -> None:
    """It is packaged with the app, not a stray directory beside it."""
    assert WEB_CLIENT_DIR == Path(__file__).resolve().parents[1] / "app" / "web"
    assert (WEB_CLIENT_DIR / "index.html").is_file()
