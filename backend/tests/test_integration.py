import uuid

import pytest

pytestmark = pytest.mark.integration
HEADERS = {"X-VGM-Request": "1", "Origin": "http://localhost:8080"}


def register(app):
    client = app.test_client()
    username = "u" + uuid.uuid4().hex[:15]
    response = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "display_name": "Test Person",
            "password": "test password 123"
        },
        headers=HEADERS
    )
    assert response.status_code == 201, response.json
    return client, response.json["user"]


def conversation(app):
    a, alice = register(app)
    b, bob = register(app)
    response = a.post(
        "/api/conversations", json={"recipient_id": bob["id"]}, headers=HEADERS
    )
    assert response.status_code == 201, response.json
    return a, alice, b, bob, response.json["id"]


def test_auth_profile_search_and_revocation(gateway):
    client, user = register(gateway)
    assert client.get("/api/me").json["user"]["id"] == user["id"]
    changed = client.patch(
        "/api/me",
        json={
            "display_name": "New Name",
            "bio": "Hello world"
        },
        headers=HEADERS
    )
    assert changed.json["user"]["bio"] == "Hello world"
    other, _ = register(gateway)
    results = other.get("/api/users", query_string={
        "q": user["username"]
    }).json["users"]
    assert results[0]["display_name"] == "New Name"
    assert "password_hash" not in results[0]
    assert client.post(
        "/api/auth/logout", json={}, headers=HEADERS
    ).status_code == 200
    assert client.get("/api/me").status_code == 401
    assert client.post(
        "/api/auth/login",
        json={
            "username": user["username"],
            "password": "test password 123"
        },
        headers=HEADERS
    ).status_code == 200


def test_duplicate_username_and_wrong_password(gateway):
    client, user = register(gateway)
    response = client.post(
        "/api/auth/register",
        json={
            "username": user["username"].upper(),
            "display_name": "Duplicate",
            "password": "test password 123"
        },
        headers=HEADERS
    )
    assert response.status_code == 409
    assert client.post(
        "/api/auth/login",
        json={
            "username": user["username"],
            "password": "incorrect password"
        },
        headers=HEADERS
    ).status_code == 401


def test_conversation_is_unique_for_pair(gateway):
    a, alice, b, bob, chat = conversation(gateway)
    again = b.post(
        "/api/conversations",
        json={"recipient_id": alice["id"]},
        headers=HEADERS
    )
    assert again.json["id"] == chat
    assert a.get("/api/conversations"
                ).json["conversations"][0]["peer"]["id"] == bob["id"]


def test_send_read_and_retry_idempotency(gateway):
    a, alice, b, bob, chat = conversation(gateway)
    path = f"/api/conversations/{chat}/messages"
    data = {"client_id": str(uuid.uuid4()), "kind": "text", "text": "hello 👋"}
    first = a.post(path, json=data, headers=HEADERS)
    retry = a.post(path, json=data, headers=HEADERS)
    assert first.status_code == 201, first.json
    assert retry.json["id"] == first.json["id"]
    messages = b.get(path).json["messages"]
    assert len(messages) == 1 and messages[0]["sender_id"] == alice["id"]
    assert a.get("/api/conversations"
                ).json["conversations"][0]["last_text"] == "hello 👋"


def test_conversation_authorization_and_actor_spoofing(gateway):
    a, alice, b, bob, chat = conversation(gateway)
    outsider, _ = register(gateway)
    path = f"/api/conversations/{chat}/messages"
    assert outsider.get(path).status_code == 404
    assert outsider.post(
        path,
        json={
            "client_id": str(uuid.uuid4()),
            "text": "intrusion"
        },
        headers=HEADERS
    ).status_code == 404
    assert a.post(
        path,
        json={
            "client_id": str(uuid.uuid4()),
            "text": "spoof",
            "actor_id": bob["id"]
        },
        headers=HEADERS
    ).status_code == 400


@pytest.mark.parametrize(
    "url,platform", [
        ("https://www.youtube.com/shorts/abcdefghijk", "youtube"),
        ("https://www.instagram.com/reel/ABC123xyz/", "instagram"),
        ("https://www.tiktok.com/@person/video/7123456789012345678", "tiktok"),
    ]
)
def test_video_messages_store_playable_embeds(gateway, url, platform):
    a, _, b, _, chat = conversation(gateway)
    response = a.post(
        f"/api/conversations/{chat}/messages",
        json={
            "client_id": str(uuid.uuid4()),
            "kind": "video",
            "text": "watch this",
            "url": url
        },
        headers=HEADERS
    )
    assert response.status_code == 201, response.json
    assert response.json["video"]["platform"] == platform
    assert response.json["video"]["embed_url"].startswith("https://")
    assert b.get(f"/api/conversations/{chat}/messages"
                ).json["messages"][0]["kind"] == "video"


def test_pagination_no_gaps_or_duplicates(gateway):
    a, _, _, _, chat = conversation(gateway)
    path = f"/api/conversations/{chat}/messages"
    ids = []
    for i in range(7):
        response = a.post(
            path,
            json={
                "client_id": str(uuid.uuid4()),
                "text": f"message {i}"
            },
            headers=HEADERS
        )
        ids.append(response.json["id"])
    page = a.get(path + "?limit=3").json
    assert [m["id"] for m in page["messages"]] == ids[-3:]
    assert page["has_more"]
    page = a.get(path + f"?limit=4&before={ids[-3]}").json
    assert [m["id"] for m in page["messages"]] == ids[:4]
    assert not page["has_more"]
    assert a.get(path + "?limit=1000").status_code == 400
    newer = a.get(path + f"?after={ids[0]}&limit=3").json
    assert [m["id"] for m in newer["messages"]] == ids[1:4]
    assert newer["has_more"]
    newer = a.get(path + f"?after={ids[3]}&limit=3").json
    assert [m["id"] for m in newer["messages"]] == ids[4:]
    assert not newer["has_more"]
    assert a.get(path + f"?after={ids[0]}&before={ids[-1]}").status_code == 400


def test_csrf_missing_auth_errors_and_request_ids(gateway):
    client = gateway.test_client()
    assert client.get("/api/me").status_code == 401
    assert client.post("/api/auth/login", json={}).status_code == 403
    response = client.post(
        "/api/auth/login",
        json={},
        headers={
            **HEADERS, "Origin": "https://evil.example"
        }
    )
    assert response.status_code == 403
    assert response.json["error"]["request_id"] == response.headers[
        "X-Request-ID"]
    assert client.post(
        "/api/auth/login", json={}, headers=HEADERS
    ).status_code == 400
    assert client.post(
        "/api/auth/login",
        data="bad",
        content_type="application/json",
        headers=HEADERS
    ).status_code == 400


def test_rate_limit(gateway):
    client = gateway.test_client()
    for _ in range(15):
        assert client.post(
            "/api/auth/login", json={}, headers=HEADERS
        ).status_code == 400
    response = client.post("/api/auth/login", json={}, headers=HEADERS)
    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"


def test_health_and_metrics(gateway):
    client = gateway.test_client()
    assert client.get("/readyz").status_code == 200
    assert client.get("/healthz").status_code == 200
    assert b"vgm_http_requests_total" in client.get("/metrics").data
