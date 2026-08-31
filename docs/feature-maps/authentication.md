# Authentication and accounts

## Purpose and flow

Email/password authentication creates a `User` and its one-to-one `Player` together. Registration and login return a two-week HS256 JWT; authenticated routes derive the current user and player from its subject. Data is private per player.

## Public API

- `POST /auth/register` — email, password (8–128 characters), hunter name, IANA timezone; returns `TokenResponse` and HTTP 201.
- `POST /auth/login` — normalized email plus password; unknown email and wrong password deliberately share one error.
- `GET /auth/me` — authenticated account identity.
- Player identity/profile is exposed separately through `/players/me`.

Contracts live in `app/schemas/auth.py`; routes in `app/routers/auth.py`; dependency resolution in `app/deps.py`; JWT/password operations in `app/security.py`.

## Persistence and invariants

- `User` is in `app/models/user.py`; email is unique and stored lowercase/trimmed.
- `Player.user_id` is unique and cascades with the user.
- Registration writes both rows in one transaction.
- Timezones must be valid IANA identifiers because daily scheduling depends on them.
- Production refuses the default/short JWT secret; settings are in `app/config.py`.
- There is no refresh-token, password-reset, email-verification, social-login, or account-deletion flow yet.

## Clients

- Web: `web/src/features/auth/auth-screen.tsx`, token storage and requests in `web/src/lib/api.ts` and `web/src/hooks/use-api.tsx`.
- iOS: `AuthView.swift`, `SessionStore.swift`, `APIClient.swift`. The access token is stored in Keychain and automatically sent as a Bearer token. Sign-out deletes it.
- Local development credentials are in ignored `PROJECT_CONTEXT.md`; never copy them into source, fixtures, previews, logs, or committed documentation.

## Verification

- Primary tests: `tests/test_auth.py`, plus ownership/error cases across other API tests.
- Check duplicate email, normalization, invalid timezone, short password, incorrect credentials, expired/invalid token, and cross-player access.
- For iOS, use `$harness`; verify a fresh registration, returning login, relaunch persistence, 401 handling, and sign-out.
