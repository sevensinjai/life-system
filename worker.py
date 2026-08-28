"""Cloudflare Python Worker entrypoint for HTTP requests and cron jobs."""

from urllib.parse import urlparse

import asgi
from workers import WorkerEntrypoint

from app.config import Settings
from app.db import SessionLocal, configure_d1
from app.main import create_app
from app.services import broadcasting
from app.services.constellations import seed_pantheon
from app.services.daily import run_daily_reset_for_all
from app.services.side_quests import close_finished_broadcasts, dispatch_due


API_PREFIXES = (
    "/auth",
    "/players",
    "/quests",
    "/skills",
    "/quotes",
    "/side-quests",
    "/constellations",
    "/system",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
)


class Default(WorkerEntrypoint):
    """Route API traffic to FastAPI and everything else to React assets."""

    _app = None
    _configured_binding = None

    def _configure(self):
        if self._configured_binding is not self.env.DB:
            configure_d1(self.env.DB)
            self._configured_binding = self.env.DB

        if self._app is None:
            settings = Settings(
                environment="production",
                debug=False,
                web_client=False,
                cors_origins=["https://system.tomchan.uk"],
                jwt_secret=str(self.env.APP_JWT_SECRET),
            )
            self._app = create_app(settings)
        return self._app

    async def fetch(self, request):
        path = urlparse(request.url).path
        if path.startswith(API_PREFIXES):
            return await asgi.fetch(self._configure(), request, self.env)
        return await self.env.ASSETS.fetch(request)

    async def scheduled(self, controller, env, ctx):
        self._configure()
        with SessionLocal() as db:
            seed_pantheon(db)

            if controller.cron == "0 9 * * *":
                if not broadcasting.has_open_broadcast(db):
                    broadcasting.schedule_next(db)

            if controller.cron == "*/15 * * * *":
                dispatch_due(db)
                close_finished_broadcasts(db)

            run_daily_reset_for_all(db, Settings(
                environment="production",
                web_client=False,
                jwt_secret=str(env.APP_JWT_SECRET),
            ))
            db.commit()
