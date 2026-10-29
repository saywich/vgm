import httpx
import pytest

from vgm import common
from vgm import video


@pytest.mark.parametrize(
    "url,platform,video_id", [
        (
            "https://www.youtube.com/shorts/abcdefghijk?si=tracking", "youtube",
            "abcdefghijk"
        ),
        ("https://youtu.be/abcdefghijk?t=2", "youtube", "abcdefghijk"),
        (
            "https://www.youtube.com/watch?v=abcdefghijk", "youtube",
            "abcdefghijk"
        ),
        (
            "https://www.tiktok.com/@person/video/7123456789012345678?is_from_webapp=1",
            "tiktok", "7123456789012345678"
        ),
        (
            "https://www.instagram.com/reel/ABC123xyz/?igsh=tracking",
            "instagram", "ABC123xyz"
        ),
        ("https://instagram.com/reels/ABC123xyz/", "instagram", "ABC123xyz"),
    ]
)
def test_normalizes_platform_links(url, platform, video_id):
    result = video.normalize(url)
    assert result["platform"] == platform
    assert result["video_id"] == video_id
    assert "tracking" not in result["canonical_url"]
    assert result["embed_url"].startswith("https://")


@pytest.mark.parametrize(
    "url", [
        "http://www.youtube.com/shorts/abcdefghijk",
        "https://youtube.com.evil.test/shorts/abcdefghijk",
        "https://www.youtube.com@127.0.0.1/shorts/abcdefghijk",
        "https://127.0.0.1/video",
        "https://www.youtube.com:8443/shorts/abcdefghijk",
        "file:///etc/passwd",
        "https://www.instagram.com/stories/person/123",
        "https://www.tiktok.com/@person",
        "https://www.youtube.com/shorts/invalid",
        "https://user:pass@www.youtube.com/shorts/abcdefghijk",
        "https://www.youtube.com:bad/shorts/abcdefghijk",
        "https://[bad/video",
    ]
)
def test_rejects_unsupported_or_unsafe_links(url):
    with pytest.raises(common.AppError) as error:
        video.normalize(url)
    assert error.value.status == 422


def test_short_link_redirect_is_revalidated(monkeypatch):
    calls = []

    def respond(request):
        calls.append(str(request.url))
        return httpx.Response(
            302,
            headers={"location": "http://169.254.169.254/latest/meta-data"}
        )

    original = httpx.Client
    monkeypatch.setattr(
        "vgm.video.httpx.Client",
        lambda **kw: original(transport=httpx.MockTransport(respond), **kw)
    )
    with pytest.raises(common.AppError):
        video.resolve("https://vm.tiktok.com/ABC/")
    assert len(calls) == 1


def test_short_link_resolves_without_downloading_video(monkeypatch):
    calls = []

    def respond(request):
        calls.append(str(request.url))
        return httpx.Response(
            302,
            headers={
                "location":
                    "https://www.tiktok.com/@person/video/7123456789012345678"
            }
        )

    original = httpx.Client
    monkeypatch.setattr(
        "vgm.video.httpx.Client",
        lambda **kw: original(transport=httpx.MockTransport(respond), **kw)
    )
    assert video.resolve("https://vm.tiktok.com/ABC/")["platform"] == "tiktok"
    assert len(calls) == 1


def test_platform_timeout_is_actionable(monkeypatch):

    def respond(request):
        raise httpx.ReadTimeout("timeout")

    original = httpx.Client
    monkeypatch.setattr(
        "vgm.video.httpx.Client",
        lambda **kw: original(transport=httpx.MockTransport(respond), **kw)
    )
    with pytest.raises(common.AppError) as error:
        video.resolve("https://vm.tiktok.com/ABC/")
    assert error.value.status == 503
