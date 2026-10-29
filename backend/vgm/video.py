import re
from urllib import parse

import httpx

from vgm import common
from vgm import contracts
from vgm.generated import vgm_pb2_grpc

YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}
TIKTOK_HOSTS = {"tiktok.com", "www.tiktok.com", "m.tiktok.com"}
INSTAGRAM_HOSTS = {"instagram.com", "www.instagram.com"}
SHORT_HOSTS = {"vm.tiktok.com", "vt.tiktok.com"}
ALLOWED_HOSTS = YOUTUBE_HOSTS | TIKTOK_HOSTS | INSTAGRAM_HOSTS | SHORT_HOSTS
REDIRECT_STATUSES = {301, 302, 303, 307, 308}


def validated_url(url):
    try:
        parts = parse.urlsplit(url)
        valid = (
            parts.scheme == "https" and parts.hostname in ALLOWED_HOSTS and
            not parts.username and not parts.password and
            parts.port in (None, 443)
        )
    except ValueError:
        valid = False

    if not valid:
        raise common.AppError(
            422, "Use an HTTPS video link from TikTok, Instagram, or YouTube"
        )

    return parts


def normalize_youtube(parts, path):
    if parts.hostname == "youtu.be":
        video_id = path.lstrip("/")
    elif path == "/watch":
        video_id = parse.parse_qs(parts.query).get("v", [None])[0]
    else:
        match = re.fullmatch(r"/(?:shorts|embed)/([\w-]{11})", path, re.ASCII)
        video_id = match.group(1) if match else None

    if not video_id or not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        return None

    embed_url = f"https://www.youtube-nocookie.com/embed/{video_id}"
    return {
        "platform": "youtube",
        "video_id": video_id,
        "canonical_url": f"https://www.youtube.com/shorts/{video_id}",
        "embed_url": f"{embed_url}?playsinline=1&rel=0",
    }


def normalize_tiktok(path):
    match = re.fullmatch(r"/@[A-Za-z0-9_.-]+/video/(\d{10,25})", path)
    if not match:
        return None

    video_id = match.group(1)
    embed_url = f"https://www.tiktok.com/player/v1/{video_id}"
    return {
        "platform": "tiktok",
        "video_id": video_id,
        "canonical_url": f"https://www.tiktok.com{path}",
        "embed_url": f"{embed_url}?autoplay=0&rel=0",
    }


def normalize_instagram(path):
    match = re.fullmatch(r"/(?:reel|reels|p)/([A-Za-z0-9_-]{5,64})", path)
    if not match:
        return None

    video_id = match.group(1)
    category = "p" if path.startswith("/p/") else "reel"
    canonical_url = f"https://www.instagram.com/{category}/{video_id}/"
    return {
        "platform": "instagram",
        "video_id": video_id,
        "canonical_url": canonical_url,
        "embed_url": canonical_url + "embed/",
    }


def normalize(url):
    parts = validated_url(url)
    path = parts.path.rstrip("/")
    result = None

    if parts.hostname in YOUTUBE_HOSTS:
        result = normalize_youtube(parts, path)
    elif parts.hostname in TIKTOK_HOSTS:
        result = normalize_tiktok(path)
    elif parts.hostname in INSTAGRAM_HOSTS:
        result = normalize_instagram(path)

    if result:
        return result

    raise common.AppError(
        422,
        "This link does not identify a supported video. "
        "Paste a TikTok video, Instagram Reel, or YouTube Shorts link",
    )


def resolve_redirects(url):
    with httpx.Client(
        timeout=2, follow_redirects=False, trust_env=False
    ) as client:
        for _ in range(4):
            validated_url(url)
            with client.stream(
                "GET", url, headers={"User-Agent": "VGM/1.0"}
            ) as response:
                if response.status_code not in REDIRECT_STATUSES:
                    break

                location = response.headers.get("location")
                if not location:
                    raise common.AppError(
                        422, "The video share link has no destination"
                    )

                url = parse.urljoin(url, location)
                validated_url(url)

            try:
                return normalize(url)
            except common.AppError:
                pass

    return normalize(url)


def resolve(url):
    parts = validated_url(url)
    is_short_link = parts.hostname in SHORT_HOSTS or (
        parts.hostname in {"www.tiktok.com", "tiktok.com"} and
        parts.path.startswith("/t/")
    )
    if not is_short_link:
        return normalize(url)

    try:
        return resolve_redirects(url)
    except httpx.HTTPError:
        raise common.AppError(
            503,
            "The video platform could not be reached. Try the full video URL",
        ) from None


class Video(vgm_pb2_grpc.VideoServicer):

    @common.rpc(contracts.Resolve)
    def Resolve(self, data):
        return resolve(data.url)
