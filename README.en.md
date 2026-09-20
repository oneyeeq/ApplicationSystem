*[Русская версия](README.md)*

# Request Service

A production-style service-request platform: a Telegram bot for customers and admins, a FastAPI backend, and a scheduler for housekeeping — all running behind a real authentication layer, not a demo stub.

Customers submit service requests through a Telegram bot. Admins review, accept, complete, or reject them — either through the same bot or through a React web admin panel. The backend is the single source of truth for both.

Built as a portfolio project, but engineered like it has to survive contact with real users: JWT access/refresh tokens with rotation and theft detection, a separate service-to-service auth model for the bot, async SQLAlchemy + Alembic migrations, a layered bot architecture, and a test suite that includes real HTTP-level integration tests, not just mocked unit tests.

## Contents

- [Architecture](#architecture)
- [Key engineering decisions](#key-engineering-decisions)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Quickstart](#quickstart)
- [Configuration](#configuration)
- [API](#api)
- [Testing](#testing)
- [Extending & scaling](#extending--scaling)
- [Roadmap](#roadmap)
- [License](#license)

## Architecture

```
                    ┌─────────────┐
   Telegram user ───▶  aiogram    │
                    │    bot      │──┐
                    └─────────────┘  │
                                      │  HTTP + X-Service-Token
                    ┌─────────────┐  │  (service-to-service auth)
  Browser / React ──▶  FastAPI    │◀─┘
   admin panel     │    API      │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐      ┌──────────────┐
                    │  PostgreSQL │◀─────│  Scheduler   │
                    │             │      │ (cleanup job)│
                    └─────────────┘      └──────────────┘
```

Four independent processes, one database, no shared in-memory state — any of them can be restarted, scaled, or redeployed without touching the others:

- **`app/`** — FastAPI backend. Owns all business logic and all writes to the database. Routes are intentionally thin (HTTP mapping + exception-to-status-code translation only); everything else lives in `services/`.
- **`bot/`** — aiogram 3 Telegram bot. Talks to the backend exclusively over HTTP, through a typed client (`bot/clients/api_client.py`) — it has no direct database access and no SQLAlchemy dependency.
- **`scheduler/`** — a standalone async loop that periodically deletes closed requests past their retention window. Talks to the database directly (no need to go through the API for a housekeeping job with no external caller).
- **`migrations/`** — Alembic migration history, one revision per schema change, all verified reversible.

## Key engineering decisions

These are the parts worth a second look if you're evaluating the code, not just skimming the folder names.

**Two separate auth models, not one stretched to fit.** A human admin logging into the (future) web panel gets a JWT access token plus a refresh token — because that's a session that needs to survive browser restarts and be revocable. The bot is a trusted service, not a person with a password, so it authenticates with a static shared secret (`X-Service-Token`, checked via `hmac.compare_digest` for timing-attack resistance) instead of pretending it's a user. See `app/dependencies/auth.py` vs `app/dependencies/service_auth.py`.

**Refresh tokens are opaque and hashed at rest, with rotation and reuse detection.** The token stored in the database is a SHA-256 hash of a random 256-bit value — never the token itself, so a database leak alone doesn't leak live sessions. Every refresh both invalidates the old token and issues a new one; if an already-used (and therefore already-revoked) token is presented again, that's treated as a signal of theft and *every* refresh token for that admin is revoked at once. See `app/services/auth_service.py::refresh_access_token`.

**Passwords use `scrypt`, refresh tokens use `sha256` — deliberately different.** A password is short and human-chosen, so it needs a slow, memory-hard hash to resist brute-forcing. A refresh token is a random 256-bit value with no brute-forceable structure; hashing it slowly would only cost CPU for no security benefit. Using the same primitive for both would be the "looks careful, isn't" version of this problem.

**The bot has almost no business logic of its own.** `bot/services/` only translates backend responses into bot-shaped `(success, message, data)` tuples and Russian-language user messages. Every actual rule (can this user submit another request, is this status transition allowed) lives once, in the backend, and both the bot and any future client see the same behavior automatically.

**The web panel keeps the access token in memory only; the refresh token lives only in the backend's httpOnly cookie.** On startup the panel silently restores the session via `POST /auth/refresh/` (the cookie goes along automatically; JS can't even read it). Any request that comes back 401 (the access token lives only 30 minutes) goes through a shared interceptor, `useApiFetch`, which refreshes the token and retries the request once before giving up and logging out. `localStorage` is deliberately never used for the token — that's the whole point, since it closes off session theft via XSS. See `admin-panel/src/api/useApiFetch.ts`.

**Tests are split by what they actually exercise.** `tests/*.py` calls service and route functions directly — fast, but blind to anything that only breaks through FastAPI's real routing, dependency injection, or Pydantic serialization. `tests/integration/*.py` sends real HTTP requests through the actual ASGI app (`httpx`/`TestClient`) against an isolated in-memory SQLite database per test. Both layers exist because they catch different classes of bugs — several real ones (an unwired `Depends`, a route path typo, a response-schema mismatch the client silently choked on) were only ever caught by the second kind, in this project's own history.

## Tech stack

| Layer | Choice |
|---|---|
| API framework | FastAPI (async), Uvicorn |
| Bot framework | aiogram 3 |
| Database | PostgreSQL 16 |
| ORM / migrations | SQLAlchemy 2.0 (async), Alembic |
| Auth | JWT (`python-jose`), `scrypt` password hashing, HMAC service tokens |
| Validation | Pydantic v2 |
| Testing | pytest, pytest-asyncio, httpx |
| Runtime | Python 3.12, Docker / Docker Compose |
| Web panel | React 19 + TypeScript, Vite, React Router, CSS Modules |

## Project structure

```
app/                  FastAPI backend
  routes/              thin HTTP layer — request/response mapping only
  services/            business logic, one module per domain (auth, admin, user, request, notification)
  models/              SQLAlchemy models
  schemas/             Pydantic request/response schemas
  dependencies/         auth.py (JWT), service_auth.py (bot service token)
  security.py          password hashing, JWT encode/decode
  database.py          engine, session factory

bot/                  aiogram Telegram bot
  handlers/            Telegram-facing entry points (commands, callbacks)
  services/            translates API responses into bot-shaped results
  clients/api_client.py  typed HTTP client — the bot's only path to the backend
  middlewares/         admin-auth middleware (checks admin status once per update)
  keyboards/, presenters/, dtos.py

scheduler/            background cleanup job
migrations/            Alembic revisions
requirements/          split per service (base/api/bot/scheduler/dev) — each Docker image installs only what it needs
docker/                one Dockerfile per service
tests/                 unit-style tests (direct function calls)
tests/integration/      HTTP-level tests against the real app
enums.py               shared status vocabulary (root-level so the bot doesn't need to import the database layer just to read an enum)

admin-panel/           React + TypeScript web panel (SPA, Vite)
  src/api/               401 interceptor with automatic access-token refresh
  src/auth/              auth context, route protection
  src/components/        shared shell (sidebar, tables, ErrorBoundary)
  src/pages/             Login, Requests, Admins, Users
```

## Quickstart

### Docker Compose (recommended)

```bash
cp .env.example .env
# fill in BOT_TOKEN, JWT_SECRET_KEY, SERVICE_TOKEN, POSTGRES_* — see Configuration below

docker compose up --build
```

This starts Postgres, the API (migrations run automatically on startup), the bot, the scheduler, and the web panel — five containers, one command. The API is available at `http://localhost:8000` (`/docs` for interactive OpenAPI docs), the panel at `http://localhost:5173`. The panel is built to static files (`npm run build`) and served by `nginx`, not the dev server — like the other services, it ships in its built form, not in development mode.

### Local development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # pulls in everything needed to run + test locally

cp .env.example .env   # point DATABASE_URL at a local/dockerized Postgres

alembic upgrade head
uvicorn app.main:app --reload

# in another terminal
./scripts/restart_bot.sh   # kills any stray bot process before starting a fresh one —
                            # running two pollers against the same BOT_TOKEN causes Telegram
                            # API conflicts and very confusing intermittent behavior

# in a third terminal, if you want the cleanup job running too
python -m scheduler.main
```

### Web panel (React) — developing the panel itself

If you actually want to edit the panel's code (not just use the built one), Docker gets in the way — the built image has no hot reload, unlike Vite's dev server. To develop the panel outside Docker:

```bash
cd admin-panel
npm install
npm run dev
```

Comes up on `http://localhost:5173` (the same port the container uses — don't run both at once) and talks to the API on `http://localhost:8000`. Make sure `CORS_ALLOWED_ORIGINS` in `.env` includes `http://localhost:5173` (it does by default).

## Configuration

All settings are read from environment variables (`config.py`, via `pydantic-settings`). See `.env.example` for the full list with placeholder values. The ones worth knowing about:

| Variable | Purpose |
|---|---|
| `BOT_TOKEN` | Telegram bot token from [@BotFather](https://t.me/BotFather) |
| `DATABASE_URL` | `postgresql+asyncpg://...` — note this must point at the `db` service by hostname inside Docker Compose, not `127.0.0.1` |
| `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRE_MINUTES` | Access token signing |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime |
| `SERVICE_TOKEN` | Shared secret the bot presents to the API (`X-Service-Token` header) |
| `CORS_ALLOWED_ORIGINS` | JSON list of origins allowed to call the API with credentials (for the future web panel) |
| `MAX_ACTIVE_REQUESTS` | How many open requests one user can have at once |
| `COMPLETED_REQUEST_RETENTION_DAYS`, `CLEANUP_INTERVAL_SECONDS` | Scheduler behavior |

Generate secrets with:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## API

Interactive docs are auto-generated by FastAPI and available at `/docs` (Swagger UI) and `/redoc` once the API is running.

At a glance:

| Endpoint | Auth | Purpose |
|---|---|---|
| `POST /auth/login/` | — | Admin login → access token (body) + refresh token (httpOnly cookie) |
| `POST /auth/refresh/` | refresh cookie | Rotate access + refresh token |
| `POST /auth/logout/` | refresh cookie | Revoke the current session |
| `GET/POST/PUT/DELETE /admins/*` | JWT | Full admin-account lifecycle (self-deletion blocked) |
| `GET /admins/active` | service token | Bot-only: active admins with a linked Telegram account, for notification routing |
| `GET/POST/PUT/DELETE /requests/*` | service token **or** JWT | Request lifecycle — usable by both the bot and the web panel |
| `GET/POST/PUT/DELETE /users/*` | service token **or** JWT | User records — usable by both the bot and the web panel (deletion blocked if the user has requests) |
| `GET /health/` | — | Liveness + real database connectivity check |

## Testing

```bash
pytest
```

83 tests, two kinds:

- **Unit-style** (`tests/`) — service, route, presenter, middleware, and bot-service logic, tested by calling functions directly with mocked dependencies. Fast, and precise about which unit is broken when one fails.
- **Integration** (`tests/integration/`) — real HTTP requests through the actual FastAPI app (`httpx`/`TestClient`) against an isolated in-memory SQLite database created fresh per test. Covers the full login → refresh (rotation + reuse-detection) → logout flow, protected-route access control, and service-token enforcement — the things that only break at the wiring level, not inside any single function.

## Extending & scaling

**Adding a new domain** (e.g. a new resource beyond users/requests/admins): add a model + migration, a `services/<domain>.py` with the business rules, a `schemas/<domain>_schemas.py`, and a thin `routes/<domain>_routes.py` that only maps exceptions to HTTP status codes. This is the same shape every existing domain already follows — nothing to invent.

**Adding a new bot flow**: a handler in `bot/handlers/`, a service function in `bot/services/` that calls the API client and returns a `(success, message, data)` tuple, and a keyboard if it needs one. Business rules still belong in the backend, not here — the bot should stay a thin presentation layer.

**Running multiple API replicas**: the API is stateless — no in-memory session state, refresh tokens live in Postgres, not in a process-local cache — so it's safe to run several instances behind a load balancer without any code changes. The bot, by contrast, must stay a single instance per `BOT_TOKEN` (Telegram's long-polling API only allows one active poller at a time; see `bot/main.py`'s file-lock guard).

**Swapping infrastructure**: Postgres, the JWT secret, and the service token are all just environment variables — pointing `DATABASE_URL` at a managed database (RDS, Cloud SQL, etc.) instead of the bundled container requires no code changes.

**Adding a new page to the panel**: a page under `admin-panel/src/pages/` that uses `useApiFetch()` for requests (the interceptor adds `Authorization` and handles token expiry on its own) and `useAuth()` for the current session. Register the route in `App.tsx` inside `ProtectedRoute`, add a link in the `Layout.tsx` sidebar. Neither auth nor 401 handling needs reinventing — that's already shared infrastructure.

## Roadmap

- [ ] Rate limiting on `POST /auth/login/` — nothing currently stops unlimited password-guessing attempts
- [ ] `secure=True` on the refresh-token cookie once deployed behind HTTPS (currently just `httponly`+`samesite=lax`, which is correct for local HTTP development)
- [ ] Pagination on list endpoints (not yet needed at current data volume)
- [ ] Archiving closed requests instead of hard-deleting them — a separate archive table so `user`/`request` can be cleaned up without losing history (not yet designed)

## License

Not yet decided — pick one before treating this as open source (MIT is the common default for portfolio projects; something more restrictive if you intend to keep commercial rights).
