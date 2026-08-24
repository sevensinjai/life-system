"""Application factory and the ASGI entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, get_settings
from app.errors import register_error_handlers
from app.routers import auth, health, players, quests, quotes, skills, system


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
    app.include_router(skills.router)
    app.include_router(system.router)

    return app


app = create_app()
