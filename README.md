# Vertical Generation Messenger

A React + TypeScript PWA for one-to-one conversations and in-chat vertical videos from TikTok, Instagram, and YouTube.

## Run with Docker

Requires Docker Engine/Desktop with Compose v2. From this directory:

```sh
cp .env.example .env
docker compose up -d --build
```

- App: **http://localhost:8080**
- Grafana: **http://localhost:3000** (local defaults: `admin` / `vertical-local-change-me`)
- Jaeger: **http://localhost:16686**

Use `localhost` consistently: `PUBLIC_ORIGIN` must match the browser origin. The first build downloads dependencies and observability images. PostgreSQL becomes healthy before the one-shot Alembic migration runs; services start only after their dependencies are ready.

Create an account, then create another in a separate browser profile/private window. Search for the other username using **Start a conversation**. Send text, paste a video URL into the composer, or use the attachment button. There are no seeded accounts or fake conversations.

```sh
docker compose ps
docker compose logs -f gateway identity messaging video
docker compose down               # retain database and observability volumes
```

The ports bind to loopback. For a remote deployment, configure an HTTPS reverse proxy, set `PUBLIC_ORIGIN=https://your-host`, set `COOKIE_SECURE=true`, and change all default passwords. Use URL-safe PostgreSQL credentials or percent-encode reserved characters in the connection URL. Only expose the frontend; the gRPC services trust calls from the private application network. Do not publish their ports. The local Compose deployment is not a hardened multi-tenant production environment.

## Features

- Registration and sign-in with case-insensitive unique usernames, scrypt password hashes, opaque seven-day sessions stored as SHA-256 hashes, HttpOnly/SameSite cookies, and logout revocation.
- Profile editing and authenticated people search. Password hashes and session tokens never appear in public user objects.
- Unique direct conversations with server-side membership checks, text/caption validation, paginated message history, live polling, and idempotent message retries using a client UUID.
- In-chat platform video players that load when you press Play. Link normalization strips tracking parameters and validates hosts, ports, paths, and video IDs. TikTok short share links use bounded, allowlisted redirects with timeouts.
- Responsive Material 3 UI using Google's official `@material/web` components through React wrappers; separate neutral light/dark palettes, blue accents, system theme detection, and accessible forms/dialogs.
- Installable PWA manifest, PNG app icons, offline app shell, and a Web Share Target. Incoming video URLs survive sign-in and wait for the user to select a conversation and press Send.
- Central JSON errors with appropriate HTTP status codes and request IDs, structured service logs, HTTP metrics, and distributed Flask → gRPC traces.

## Architecture

```text
Browser / installed PWA
          │ HTTP, same-origin /api
     Nginx + React assets
          │ REST
      Flask gateway ───────────────┐
          │ gRPC                  │ OpenTelemetry
   ┌──────┼──────────┐            ▼
Identity  Messaging  Video       Jaeger
   ▲         │          
   └──gRPC───┤──gRPC────┘
   │         │
   └── PostgreSQL ──┘
       separate schemas

Gateway /metrics → Prometheus → Grafana
Container JSON logs → Alloy → Loki → Grafana → Jaeger trace links
```

The Python services communicate through explicit RPCs in `proto/vgm.proto`. Protobuf carries JSON envelopes with Pydantic request contracts, keeping validation consistent at REST and RPC boundaries. The gateway derives `actor_id` from the session, never from a user-supplied field. Messaging looks up public profiles through Identity and resolves video messages through Video. Video metadata is stored with each message.

Identity owns the `identity` schema; Messaging owns `messaging`. There are no cross-service SQL joins or ORM models. Alembic uses SQLAlchemy only as its DDL transport; application database access is parameterized psycopg SQL. A shared PostgreSQL instance and migration job keep the MVP deployment manageable.

| Component | Source | Internal port |
| --- | --- | --- |
| REST gateway | `backend/vgm/gateway.py` | 8000 |
| Identity | `backend/vgm/identity.py` | 50051 |
| Messaging | `backend/vgm/messaging.py` | 50051 |
| Video resolution | `backend/vgm/video.py` | 50051 |
| React PWA | `frontend/src/` | Nginx 80 |
| DB migrations | `backend/migrations/` | — |
| Observability | `deploy/` | — |

## REST API

All mutations require `Content-Type: application/json` and `X-VGM-Request: 1`. Browser origins are checked against `PUBLIC_ORIGIN`; CORS is not enabled. Authenticated endpoints use the `vgm_session` cookie.

| Method / path | Body or query | Result |
| --- | --- | --- |
| `POST /api/auth/register` | `username`, `display_name`, `password` | 201 + user + session cookie |
| `POST /api/auth/login` | `username`, `password` | user + session cookie |
| `POST /api/auth/logout` | `{}` | revoke session |
| `GET /api/me` | — | current user |
| `PATCH /api/me` | `display_name`, `bio` | updated user |
| `GET /api/users?q=…` | nonempty search, up to 60 characters | up to 30 people |
| `GET /api/conversations` | — | latest 100 conversations, with peers and previews |
| `POST /api/conversations` | `recipient_id` UUID | existing or new direct conversation |
| `GET /api/conversations/:id/messages` | `before` or `after` ID, `limit` (1–100, default 50) | ascending page + `has_more` |
| `POST /api/conversations/:id/messages` | `client_id` UUID, `kind`, `text`, optional `url` | persisted message |
| `POST /api/videos/resolve` | `url` | platform, ID, canonical URL, embed URL |

Text messages require nonblank `text`; video messages require `url` and may include caption `text`. Reuse the same `client_id` only when retrying the same send. Unknown fields are rejected.

Errors: 400 invalid request, 401 unauthenticated, 403 CSRF/origin violation, 404 missing or inaccessible resource, 409 duplicate username, 413 oversized body, 415 unsupported content type, 422 unsupported video/content, 429 rate limited, 500 internal failure, 503 unavailable service, 504 upstream timeout. Errors have the shape:

```json
{"error":{"status":400,"message":"Human-readable explanation","request_id":"uuid"}}
```

Proxy-generated 413/503 errors have the same error envelope without a request ID. `/healthz`, `/readyz`, and `/metrics` are internal gateway endpoints; Nginx does not publish them. The MVP login/register limit is 15 requests per source IP per minute, maintained by the single gateway worker. Use a shared rate-limit store before scaling gateway workers/replicas.

## Local development

Python 3.12+, Node 22+, and PostgreSQL 17 recommended.

```sh
python3.12 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
sh scripts/generate-proto.sh
export DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/vgm
alembic -c backend/alembic.ini upgrade head
python scripts/dev.py
```

In another terminal:

```sh
cd frontend
npm ci
npm run dev
```

Open **http://localhost:5173**. Vite proxies `/api` to the local gateway. Local backend ports are 50051 (Identity), 50052 (Video), and 50053 (Messaging). Stop the backend runner with Ctrl+C. Service worker registration is production-only so it cannot cache development source.

## Tests

```sh
. .venv/bin/activate
sh scripts/generate-proto.sh
python -m pytest -q -m 'not integration'
TEST_DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/vgm_test python -m pytest -q
cd frontend && npm ci && npm run build
docker compose config --quiet
```

Use a **dedicated test database**. Integration tests apply migrations, create random test users/messages, and start real gRPC services on temporary ports. They exercise the REST gateway against PostgreSQL, including membership isolation, cookie/session lifecycle, idempotency, validation, pagination, rate limits, and video embeds. Without `TEST_DATABASE_URL`, integration tests explicitly skip. CI provisions PostgreSQL and runs the entire suite plus the frontend build.

## Observability

Grafana provisions Prometheus, Loki, Jaeger, and the **Vertical / Overview** dashboard. It shows request rates, p95 latency, server errors, and JSON service logs. Expand a log's `trace_id` to follow the request into Jaeger. Request bodies, passwords, and session tokens are not logged by the application. Alloy collects Docker logs through the local Docker socket; this is a trusted local operator deployment. Loki has seven-day retention; PostgreSQL, Grafana, Jaeger, Prometheus, Loki, and Alloy use named volumes.

## Platform and MVP boundaries

- Playback uses official platform-hosted embeds, not scraped/downloaded video files. Public embeddable videos play within the chat; deleted/private/age-restricted videos, regional restrictions, platform cookies, or disabled embedding may prevent playback. A per-video help panel offers the original URL as a fallback. Instagram may show platform chrome or a sign-in prompt. This app cannot override those restrictions.
- Supported inputs: TikTok `/@user/video/:id` plus `vm`, `vt`, and `/t/` short links; Instagram `/reel/`, `/reels/`, `/p/`; YouTube `/shorts/`, `youtu.be`, and `/watch?v=`. Instagram redirect-style share URLs and stories are not supported; use the Reel's direct link. YouTube watch links do not guarantee vertical orientation.
- Web Share Target support depends on the browser/OS and usually requires installing the PWA over HTTPS (localhost is allowed). On browsers without it, paste the link directly. This is URL sharing, not video-file upload.
- Offline mode caches only the public app shell and static assets. Private conversations are never cached by the service worker; sending and reading messages require a connection. There is no offline send queue, push notifications, group chat, unread receipts, password reset, moderation, or end-to-end encryption in this MVP.
- Live delivery uses 2.5-second message polling and 4-second conversation polling. History loads 50 messages initially, with earlier-page loading; cursor-based polling catches up without dropping messages after interruptions. The conversation list is capped at the latest 100.

Platform references: [TikTok Embed Player](https://developers.tiktok.com/docs/en/embed-player), [YouTube embedded players](https://developers.google.com/youtube/player_parameters), [Instagram embeds](https://developers.facebook.com/docs/instagram-platform/oembed), [Material Web](https://material-web.dev/).

## Python formatting

Python source follows Google-style imports, four-space indentation, an 80-column target, and blank lines between logical steps. RPC method names retain the casing required by the generated gRPC interface. Source comments and docstrings are omitted as requested; generated bindings are cleaned automatically after protoc runs.

```sh
pip install -e '.[dev]'
make format
make check-format
```

YAPF, isort, and pytest use the settings in `pyproject.toml`. Generated bindings are excluded from manual formatting. The reference is the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).

## Theme palettes

`frontend/PALETTES.md` lists the light and dark colors. The separate CSS palettes live in `frontend/src/themes/`. Surfaces use neutral grays; blue accents appear only on actions, links, focus indicators, and icons. Choose System, Light, or Dark from the theme selector.

## Python dependencies

`pyproject.toml` is the single dependency and tooling configuration file. It preserves the pinned versions from the previous dependency files. Runtime dependencies are under `[project.dependencies]`; testing and formatting tools are in the `dev` extra.

```sh
python -m pip install .
python -m pip install -e '.[dev]'
```

The first command installs the backend package and runtime dependencies. The second installs an editable checkout with development tools. Run these commands from the repository root. Python 3.12 or newer is required.

Generated protobuf bindings are included in the source package so a regular installation works without a separate generation step. After modifying `proto/vgm.proto`, run `sh scripts/generate-proto.sh` before building a distribution. Docker also regenerates the bindings and runs against the copied backend source.
