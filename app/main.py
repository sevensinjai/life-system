"""Application factory and the ASGI entrypoint."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.config import Settings, get_settings
from app.errors import register_error_handlers
from app.routers import auth, health, players, quests, quotes, system

WEB_CLIENT_DIR = Path(__file__).parent / "web"


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build a configured application instance.

    Tests call this directly so they can pass their own settings instead of
    depending on whatever the environment happens to hold.
    """
    override = settings is not None
    settings = settings or get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        debug=settings.debug,
        description=(
            "A real-life RPG System: quests, EXP, levels, stats, "
            "and penalties for the dailies you skip."
        ),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if override:
        # Routes depend on get_settings; point it at the instance we were handed.
        app.dependency_overrides[get_settings] = lambda: settings

    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(players.router)
    app.include_router(quests.router)
    app.include_router(quotes.router)
    app.include_router(system.router)

    if settings.web_client:
        mount_web_client(app)

    return app


def mount_web_client(app: FastAPI) -> None:
    """Serve the browser client at /web, and send / to it.

    The iOS app is the real client; this is a hand-testing stand-in for it.
    Static files only — no build step and no server-side rendering — so it
    ships with the API and talks to it over the same public endpoints.
    """
    if not WEB_CLIENT_DIR.is_dir():  # pragma: no cover - a trimmed install
        return

    @app.get("/", include_in_schema=False)
    async def web_client_root() -> RedirectResponse:
        return RedirectResponse("/web/")

    app.mount(
        "/web",
        StaticFiles(directory=WEB_CLIENT_DIR, html=True),
        name="web",
    )


app = create_app()
