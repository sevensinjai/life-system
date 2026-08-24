# cat-only-svg

Backend API skeleton — FastAPI, Python 3.11+.

This is scaffolding only: a configured app factory, health endpoint, error
handling, settings, and tests. Domain routes go in `app/routers/`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Interactive docs: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

## Test

```bash
pytest
```

## Layout

```
app/
  main.py           # create_app() factory + `app` ASGI entrypoint
  config.py         # Settings (pydantic-settings), get_settings()
  errors.py         # AppError hierarchy + JSON error handlers
  routers/
    health.py       # GET /health
tests/
  conftest.py       # settings + client fixtures
  test_health.py
  test_errors.py
```

## Configuration

Settings load from environment variables with the `APP_` prefix, or from a
local `.env`. Copy `.env.example` to `.env` to start.

| Variable           | Default             | Notes                                    |
| ------------------ | ------------------- | ---------------------------------------- |
| `APP_APP_NAME`     | `cat-only-svg-api`  | Shown in OpenAPI title and `/health`     |
| `APP_ENVIRONMENT`  | `development`       | `development` \| `test` \| `production`  |
| `APP_DEBUG`        | `false`             | FastAPI debug mode                       |
| `APP_HOST`         | `127.0.0.1`         |                                          |
| `APP_PORT`         | `8000`              |                                          |
| `APP_CORS_ORIGINS` | `["*"]`             | JSON list of allowed origins             |

`APP_CORS_ORIGINS` defaults to `["*"]`, which is fine locally but should be
narrowed to your real frontend origins before deploying.

## Adding a route

Create a module in `app/routers/`, define an `APIRouter`, and register it in
`create_app`:

```python
# app/routers/cats.py
from fastapi import APIRouter

from app.errors import NotFoundError

router = APIRouter(prefix="/cats", tags=["cats"])


@router.get("/{cat_id}")
async def get_cat(cat_id: str) -> dict:
    raise NotFoundError(f"No cat with id {cat_id!r}.")
```

```python
# app/main.py
from app.routers import cats, health

app.include_router(health.router)
app.include_router(cats.router)
```

## Errors

Raise `AppError` or a subclass (`NotFoundError`, `ValidationError`) instead of
building responses by hand. Handlers render every failure — including
unmatched routes and request-validation failures — in one shape:

```json
{ "error": { "code": "not_found", "message": "No cat with id 'tabby'." } }
```

Validation failures add a `details` array with the offending fields.
