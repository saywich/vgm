import collections
import logging
import os
import threading
import time
import uuid

import flask
import grpc
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc
from opentelemetry.instrumentation import flask as flask_instrumentation
import prometheus_client
import pydantic
from werkzeug import exceptions

from vgm import common
from vgm import contracts
from vgm import observability

SESSION_COOKIE = "vgm_session"
AUTH_PATHS = {"/api/auth/login", "/api/auth/register"}
AUTH_WINDOW_SECONDS = 60
AUTH_REQUEST_LIMIT = 15

REQUESTS = prometheus_client.Counter(
    "vgm_http_requests_total",
    "REST requests",
    ["method", "route", "status"],
)
LATENCY = prometheus_client.Histogram(
    "vgm_http_request_duration_seconds",
    "REST latency",
    ["route"],
)
attempts = collections.defaultdict(collections.deque)
rate_lock = threading.Lock()

observability.configure("gateway")
app = flask.Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16384
flask_instrumentation.FlaskInstrumentor().instrument_app(app)

identity = common.client("identity")
messaging = common.client("messaging")
video = common.client("video")


def validate(contract, data=None):
    if data is None:
        data = flask.request.get_json()

    return contract.model_validate(data).model_dump(mode="json")


def actor():
    return flask.g.user["id"]


def enforce_origin():
    if flask.request.method in {"GET", "HEAD", "OPTIONS"}:
        return

    if flask.request.headers.get("X-VGM-Request") != "1":
        raise common.AppError(403, "The request is missing CSRF protection")

    origin = flask.request.headers.get("Origin")
    allowed_origin = os.getenv("PUBLIC_ORIGIN", "http://localhost:8080")
    if origin and origin != allowed_origin:
        raise common.AppError(403, "This origin is not allowed")


def limit_auth_requests():
    address = flask.request.remote_addr or "unknown"
    key = flask.request.headers.get("X-Real-IP", address)
    now = time.monotonic()
    cutoff = now - AUTH_WINDOW_SECONDS

    with rate_lock:
        stale_keys = [
            address for address, hits in attempts.items()
            if not hits or hits[-1] < cutoff
        ]
        for stale_key in stale_keys:
            del attempts[stale_key]

        hits = attempts[key]
        while hits and hits[0] < cutoff:
            hits.popleft()

        if len(hits) >= AUTH_REQUEST_LIMIT:
            raise common.AppError(
                429, "Too many sign-in attempts. Try again in a minute"
            )

        hits.append(now)


@app.before_request
def before():
    flask.g.request_id = str(uuid.uuid4())
    flask.g.started = time.monotonic()

    if not flask.request.path.startswith("/api/"):
        return

    enforce_origin()
    if flask.request.path in AUTH_PATHS:
        limit_auth_requests()
        return

    token = flask.request.cookies.get(SESSION_COOKIE)
    if not token:
        raise common.AppError(401, "Please sign in to continue")

    flask.g.user = common.call(identity, "Authenticate", {"token": token})


@app.after_request
def after(response):
    elapsed = time.monotonic() - flask.g.get("started", time.monotonic())
    rule = flask.request.url_rule
    route = rule.rule if rule else "unmatched"

    REQUESTS.labels(flask.request.method, route, response.status_code).inc()
    LATENCY.labels(route).observe(elapsed)

    response.headers["X-Request-ID"] = flask.g.get("request_id", "")
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"

    logging.info(
        "http_request",
        extra={
            "request_id": flask.g.get("request_id"),
            "method": flask.request.method,
            "route": route,
            "status": response.status_code,
            "duration_ms": round(elapsed * 1000, 2),
        },
    )
    return response


def error_details(exc):
    if isinstance(exc, common.AppError):
        return exc.status, exc.message

    if isinstance(exc, pydantic.ValidationError):
        details = [
            f"{'.'.join(map(str, error['loc']))}: {error['msg']}"
            for error in exc.errors()
        ]
        return 400, "; ".join(details)

    if isinstance(exc, grpc.RpcError):
        status = common.GRPC_TO_HTTP.get(exc.code(), 500)
        if status < 500:
            return status, exc.details()
        return status, "A service is temporarily unavailable. Please try again"

    if isinstance(exc, exceptions.HTTPException):
        return exc.code, exc.description

    logging.exception("gateway_failed")
    return 500, "An unexpected error occurred"


@app.errorhandler(Exception)
def error(exc):
    status, message = error_details(exc)
    response = flask.jsonify(
        {
            "error":
                {
                    "message": message,
                    "status": status,
                    "request_id": flask.g.get("request_id", ""),
                }
        }
    )

    if status == 429:
        response.headers["Retry-After"] = str(AUTH_WINDOW_SECONDS)

    return response, status


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.get("/readyz")
def ready():
    for name in ("identity", "messaging", "video"):
        address = os.getenv(f"{name.upper()}_ADDRESS", f"{name}:50051")
        with grpc.insecure_channel(address) as channel:
            stub = health_pb2_grpc.HealthStub(channel)
            result = stub.Check(health_pb2.HealthCheckRequest(), timeout=2)
            if result.status != health_pb2.HealthCheckResponse.SERVING:
                raise common.AppError(503, "A service is not ready")

    return {"status": "ready"}


@app.get("/metrics")
def metrics():
    return app.response_class(
        prometheus_client.generate_latest(),
        mimetype=prometheus_client.CONTENT_TYPE_LATEST,
    )


def authenticate(method, contract):
    result = common.call(identity, method, validate(contract))
    response = flask.jsonify({"user": result["user"]})
    response.set_cookie(
        SESSION_COOKIE,
        result["token"],
        max_age=60 * 60 * 24 * 7,
        httponly=True,
        secure=os.getenv("COOKIE_SECURE", "false").lower() == "true",
        samesite="Lax",
        path="/",
    )
    return response


@app.post("/api/auth/register")
def register():
    return authenticate("Register", contracts.Register), 201


@app.post("/api/auth/login")
def login():
    return authenticate("Login", contracts.Credentials)


@app.post("/api/auth/logout")
def logout():
    token = flask.request.cookies[SESSION_COOKIE]
    common.call(identity, "Logout", {"token": token})

    response = flask.jsonify({"ok": True})
    response.delete_cookie(SESSION_COOKIE, path="/")
    return response


@app.get("/api/me")
def me():
    return {"user": flask.g.user}


@app.patch("/api/me")
def update_profile():
    data = {**validate(contracts.ProfileUpdate), "actor_id": actor()}
    user = common.call(identity, "UpdateProfile", data)
    return {"user": user}


@app.get("/api/users")
def search():
    data = validate(
        contracts.Search, {
            "query": flask.request.args.get("q", ""),
            "actor_id": actor(),
        }
    )
    return common.call(identity, "Search", data)


@app.get("/api/conversations")
def conversations():
    return common.call(messaging, "Conversations", {"actor_id": actor()})


@app.post("/api/conversations")
def open_conversation():
    body = flask.request.get_json()
    if not isinstance(body, dict) or set(body) != {"recipient_id"}:
        raise common.AppError(400, "Provide a recipient_id")

    data = validate(contracts.OpenConversation, {**body, "actor_id": actor()})
    return common.call(messaging, "OpenConversation", data), 201


@app.get("/api/conversations/<uuid:conversation_id>/messages")
def messages(conversation_id):
    data = validate(
        contracts.MessageQuery, {
            "actor_id": actor(),
            "conversation_id": conversation_id,
            "before": flask.request.args.get("before"),
            "after": flask.request.args.get("after"),
            "limit": flask.request.args.get("limit", 50),
        }
    )
    return common.call(messaging, "Messages", data)


@app.post("/api/conversations/<uuid:conversation_id>/messages")
def send(conversation_id):
    data = {
        **validate(contracts.MessageBody),
        "actor_id": actor(),
        "conversation_id": str(conversation_id),
    }
    return common.call(messaging, "Send", data), 201


@app.post("/api/videos/resolve")
def resolve():
    return common.call(video, "Resolve", validate(contracts.Resolve))
