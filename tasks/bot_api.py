import asyncio
import hmac
import time
from collections import deque
from aiohttp import web

from bot_init import ss14_db
from dataConfig import BOT_API_HOST, BOT_API_PORT, BOT_API_TOKEN
from tasks.discord_auth import set_linked_role_for_discord_id


_api_runner: web.AppRunner | None = None
_api_site: web.BaseSite | None = None
_api_started = False

_RATE_LIMIT_WINDOW = 60.0
_RATE_LIMIT_MAX = 20
_LOG_THROTTLE_SECONDS = 30.0
_CONCURRENCY_LIMIT = 10

_rate_limit_ip: dict[str, deque[float]] = {}
_log_last: dict[str, float] = {}
_semaphore = asyncio.Semaphore(_CONCURRENCY_LIMIT)


def _extract_token(request: web.Request) -> str:
    auth = request.headers.get("Authorization", "").strip()
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return auth


def _build_json(ok: bool, message: str, discord_id: str | None = None) -> dict:
    return {
        "ok": ok,
        "message": message,
        "discord_id": discord_id,
    }


def _log_throttled(key: str, message: str) -> None:
    now = time.monotonic()
    last = _log_last.get(key, 0.0)
    if now - last < _LOG_THROTTLE_SECONDS:
        return
    _log_last[key] = now
    print(message)


def _check_rate_limit(bucket: dict[str, deque[float]], key: str) -> bool:
    now = time.monotonic()
    window_start = now - _RATE_LIMIT_WINDOW
    dq = bucket.get(key)
    if dq is None:
        dq = deque()
        bucket[key] = dq
    while dq and dq[0] < window_start:
        dq.popleft()
    if len(dq) >= _RATE_LIMIT_MAX:
        return False
    dq.append(now)
    return True


async def _discord_unlink_handler(request: web.Request) -> web.Response:
    expected_token = (BOT_API_TOKEN or "").strip()
    if not expected_token:
        return web.json_response(_build_json(False, "BOT_API_TOKEN не настроен."), status=503)

    request_token = _extract_token(request)
    if not request_token or not hmac.compare_digest(request_token, expected_token):
        ip = request.remote or "unknown"
        if not _check_rate_limit(_rate_limit_ip, ip):
            _log_throttled("rate_limit_ip", f"[DiscordAuthApi] Rate limit exceeded for IP {ip}")
        return web.json_response(_build_json(False, "Неверный токен авторизации."), status=401)

    ip = request.remote or "unknown"
    if not _check_rate_limit(_rate_limit_ip, ip):
        _log_throttled("rate_limit_ip", f"[DiscordAuthApi] Rate limit exceeded for IP {ip}")
        return web.json_response(_build_json(False, "Слишком много запросов."), status=429)

    async with _semaphore:
        try:
            payload = await request.json()
        except Exception as e:
            return web.json_response(_build_json(False, f"Некорректный JSON: {e}"), status=400)

        user_id = str(payload.get("user_id") or "").strip()
        discord_id = str(payload.get("discord_id") or "").strip()

        if not user_id and not discord_id:
            return web.json_response(
                _build_json(False, "Не указан user_id или discord_id."),
                status=400,
            )

        success, message, resolved_discord_id = await ss14_db.unlink_user_global(
            user_id=user_id or None,
            discord_id=discord_id or None,
        )

        if success and resolved_discord_id:
            await set_linked_role_for_discord_id(resolved_discord_id, False)

        status = 200 if success else 409
        return web.json_response(
            _build_json(success, message, resolved_discord_id),
            status=status,
        )


async def ensure_bot_api_started() -> bool:
    global _api_runner, _api_site, _api_started

    if _api_started:
        return True

    if not (BOT_API_TOKEN or "").strip():
        print("[DiscordAuthApi] BOT_API_TOKEN не задан. API глобальной отвязки не запущен.")
        return False

    app = web.Application()
    app.router.add_post("/api/v1/discord/unlink", _discord_unlink_handler)

    _api_runner = web.AppRunner(app)
    await _api_runner.setup()

    _api_site = web.TCPSite(_api_runner, BOT_API_HOST, BOT_API_PORT)
    await _api_site.start()

    _api_started = True
    print(f"[DiscordAuthApi] Started on http://{BOT_API_HOST}:{BOT_API_PORT}")
    return True
