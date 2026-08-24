"""Application factory and the ASGI entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, get_settings
from app.errors import register_error_handlers
from app.routers import health


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

    return app


app = create_app()
