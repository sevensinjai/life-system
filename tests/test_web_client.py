"""The React client the API serves for hand-testing."""

import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import WEB_CLIENT_DIR, create_app

WEB_SOURCE = Path(__file__).resolve().parents[1] / "web"
BUILT = WEB_CLIENT_DIR.is_dir()
needs_build = pytest.mark.skipif(
    not BUILT, reason="run `npm install && npm run build` in web/ to test the built client"
)

# Paths the client itself owns, which the dev server must not forward.
CLIENT_OWNED = {"/", "/web", "/docs", "/redoc", "/openapi.json"}


def api_prefixes(client: TestClient) -> set[str]:
    """The top-level path segment of every API route, e.g. `/quests`.

    Read off the OpenAPI schema rather than `app.routes`, which hands back
    opaque router objects on some FastAPI versions — a walk over those finds
    nothing and quietly asserts nothing.
    """
    paths = client.get("/openapi.json").json()["paths"]
    prefixes = {f"/{path.lstrip('/').split('/')[0]}" for path in paths}
    return prefixes - CLIENT_OWNED


def test_client_source_is_present() -> None:
    for relative in ("index.html", "package.json", "components.json", "src/lib/api.ts"):
        assert (WEB_SOURCE / relative).is_file(), relative


def test_build_script_exists() -> None:
    package = json.loads((WEB_SOURCE / "package.json").read_text())
    assert "build" in package["scripts"]


def test_client_declares_a_mobile_viewport() -> None:
    """It is a phone UI; without this meta a phone renders it desktop-scaled."""
    index = (WEB_SOURCE / "index.html").read_text()

    assert 'name="viewport"' in index
    assert "width=device-width" in index
    assert "viewport-fit=cover" in index, "safe-area insets need viewport-fit=cover"


def test_vite_builds_for_the_mount_path() -> None:
    """Local builds use /web while Cloudflare's asset binding uses root."""
    config = (WEB_SOURCE / "vite.config.ts").read_text()
    assert 'process.env.LIFE_SYSTEM_CLOUDFLARE ? "/" : "/web/"' in config


def test_dev_server_proxies_every_api_prefix(client: TestClient) -> None:
    """Otherwise a new router works in production and 404s under `npm run dev`."""
    config = (WEB_SOURCE / "vite.config.ts").read_text()
    proxied = set(re.findall(r'"(/[a-z.-]+)"', config))

    found = api_prefixes(client)
    assert "/quests" in found, "no API prefixes found; this test would assert nothing"

    missing = found - proxied
    assert not missing, f"vite.config.ts proxy is missing {sorted(missing)}"


@needs_build
def test_index_is_served(client: TestClient) -> None:
    response = client.get("/web/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert '<div id="root">' in response.text


@needs_build
def test_root_redirects_to_the_client(client: TestClient) -> None:
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/web/"


@needs_build
def test_built_assets_are_served(client: TestClient) -> None:
    """The hashed bundles the built index.html asks for must resolve under /web."""
    index = (WEB_CLIENT_DIR / "index.html").read_text()
    references = re.findall(r'(?:src|href)="(/web/[^"]+)"', index)

    assert references, "built index.html references no bundles"
    for reference in references:
        assert client.get(reference).status_code == 200, reference


def test_missing_build_is_not_an_error(monkeypatch, session_factory) -> None:
    """A source checkout with no `npm run build` still serves the API."""
    monkeypatch.setattr("app.main.WEB_CLIENT_DIR", WEB_SOURCE / "does-not-exist")
    app = create_app(_settings())

    with TestClient(app, raise_server_exceptions=False) as unbuilt:
        assert unbuilt.get("/web/").status_code == 404
        assert unbuilt.get("/", follow_redirects=False).status_code == 404
        assert unbuilt.get("/health").status_code == 200


def test_client_can_be_disabled(session_factory) -> None:
    """An app-only deployment turns the whole thing off."""
    app = create_app(_settings(web_client=False))

    with TestClient(app, raise_server_exceptions=False) as disabled:
        assert disabled.get("/web/").status_code == 404
        assert disabled.get("/", follow_redirects=False).status_code == 404
        assert disabled.get("/health").status_code == 200


def _settings(**overrides) -> Settings:
    return Settings(
        environment="test",
        jwt_secret="test-secret-that-is-long-enough-for-hs256",
        database_url="sqlite://",
        **overrides,
    )
