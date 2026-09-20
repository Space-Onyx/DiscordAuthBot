import asyncio
import hashlib
import hmac
import time
from collections import deque
from uuid import UUID
from aiohttp import web

import disnake

from bot_init import bot, ss14_db
from dataConfig import BOT_API_HOST, BOT_API_PORT, BOT_API_TOKEN, get_ahelp_notify_target, get_ban_notify_target, get_round_notify_target, get_server_label
from notifications_utils import build_ahelp_embed, build_ban_embed, build_role_ping_content, build_round_embed
from tasks.discord_auth import set_linked_role_for_discord_id


_api_runner: web.AppRunner | None = None
_api_site: web.BaseSite | None = None
_api_started = False

_RATE_LIMIT_WINDOW = 60.0
_RATE_LIMIT_MAX = 20
_LOG_THROTTLE_SECONDS = 30.0
_CONCURRENCY_LIMIT = 10
_AHELP_STATE_LIMIT = 1000
_AHELP_CONVERSATIONS_LIMIT = 100

_rate_limit_ip: dict[str, deque[float]] = {}
_log_last: dict[str, float] = {}
_semaphore = asyncio.Semaphore(_CONCURRENCY_LIMIT)


def _extract_token(request: web.Request) -> str:
    auth = request.headers.get("Authorization", "").strip()
    if " " in auth:
        return auth.split(" ", 1)[1].strip()
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
    if len(bucket) > 10000:
        for stale_key, values in list(bucket.items()):
            if not values or values[-1] < window_start:
                bucket.pop(stale_key, None)
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
            return web.json_response(_build_json(False, "Слишком много запросов."), status=429)
        return web.json_response(_build_json(False, "Неверный токен авторизации."), status=401)

    ip = request.remote or "unknown"
    if not _check_rate_limit(_rate_limit_ip, ip):
        _log_throttled("rate_limit_ip", f"[DiscordAuthApi] Rate limit exceeded for IP {ip}")
        return web.json_response(_build_json(False, "Слишком много запросов."), status=429)

    async with _semaphore:
        try:
            payload = await request.json()
        except Exception:
            return web.json_response(_build_json(False, "Некорректный JSON."), status=400)
        if not isinstance(payload, dict):
            return web.json_response(_build_json(False, "Ожидается JSON-объект."), status=400)

        user_id = str(payload.get("user_id") or "").strip()
        discord_id = str(payload.get("discord_id") or "").strip()

        if not user_id and not discord_id:
            return web.json_response(
                _build_json(False, "Не указан user_id или discord_id."),
                status=400,
            )
        try:
            if user_id:
                UUID(user_id)
        except ValueError:
            return web.json_response(_build_json(False, "Некорректный user_id."), status=400)
        if discord_id and (not discord_id.isdigit() or len(discord_id) > 20):
            return web.json_response(_build_json(False, "Некорректный идентификатор."), status=400)

        try:
            success, message, resolved_discord_id = await ss14_db.unlink_user_global(
                user_id=user_id or None,
                discord_id=discord_id or None,
            )
        except Exception as error:
            print(f"[DiscordAuthApi] unlink error={error}")
            return web.json_response(_build_json(False, "БД временно недоступна."), status=503)

        if success and resolved_discord_id:
            await set_linked_role_for_discord_id(resolved_discord_id, False)

        status = 200 if success else 409
        return web.json_response(
            _build_json(success, message, resolved_discord_id),
            status=status,
        )


# Состояние опубликованных ахелп-обращений: message ID и хеш текста.
_ahelp_messages: dict[tuple[str, str], dict] = {}

_ROUND_EVENT_TYPES = ("lobby", "started", "ended")


def _require_bot_token(request: web.Request) -> bool:
    expected_token = (BOT_API_TOKEN or "").strip()
    if not expected_token:
        return False

    request_token = _extract_token(request)
    return bool(request_token) and hmac.compare_digest(request_token, expected_token)


def _check_bot_api_access(request: web.Request) -> web.Response | None:
    if not (BOT_API_TOKEN or "").strip():
        return web.json_response({"ok": False, "message": "BOT_API_TOKEN не настроен."}, status=503)

    if not _require_bot_token(request):
        ip = request.remote or "unknown"
        if not _check_rate_limit(_rate_limit_ip, ip):
            _log_throttled("rate_limit_ip", f"[DiscordAuthApi] Rate limit exceeded for IP {ip}")
            return web.json_response({"ok": False, "message": "Слишком много запросов."}, status=429)
        return web.json_response({"ok": False, "message": "Неверный токен авторизации."}, status=401)

    ip = request.remote or "unknown"
    if not _check_rate_limit(_rate_limit_ip, ip):
        _log_throttled("rate_limit_ip", f"[DiscordAuthApi] Rate limit exceeded for IP {ip}")
        return web.json_response({"ok": False, "message": "Слишком много запросов."}, status=429)

    return None


async def _resolve_notify_channel(channel_id: int):
    channel = bot.get_channel(channel_id)
    if channel is None:
        channel = await bot.fetch_channel(channel_id)
    return channel


async def _round_event_handler(request: web.Request) -> web.Response:
    denied = _check_bot_api_access(request)
    if denied is not None:
        return denied

    async with _semaphore:
        try:
            payload = await request.json()
        except Exception:
            return web.json_response({"ok": False, "message": "Некорректный JSON."}, status=400)
        if not isinstance(payload, dict):
            return web.json_response({"ok": False, "message": "Ожидается JSON-объект."}, status=400)

        event_type = str(payload.get("type") or "")
        if event_type not in _ROUND_EVENT_TYPES:
            return web.json_response(
                {"ok": False, "message": f"Неизвестный тип события: {event_type}."},
                status=400,
            )

        target = get_round_notify_target(payload.get("serverName"))
        if target is None:
            return web.json_response(
                {"ok": False, "message": "Сервер не распознан или ROUND_CHANNEL не настроен."},
                status=404,
            )

        server, channel_id, ping_role = target

        try:
            channel = await _resolve_notify_channel(channel_id)
        except Exception as error:
            print(f"[RoundNotify] channel={channel_id} error={error}")
            return web.json_response({"ok": False, "message": "Канал недоступен."}, status=404)

        embed = build_round_embed(payload, get_server_label(server, payload.get("serverName")))
        # Пинг роли всегда вне embed. Пингуем только о конце раунда, как раньше через вебхуки.
        content = build_role_ping_content(ping_role) if event_type == "ended" else None

        try:
            await channel.send(content=content, embed=embed)
        except Exception as error:
            print(f"[RoundNotify] channel={channel_id} send error={error}")
            return web.json_response({"ok": False, "message": "Не удалось отправить уведомление."}, status=502)

        return web.json_response({"ok": True, "message": "ok"})


async def _ahelp_event_handler(request: web.Request) -> web.Response:
    denied = _check_bot_api_access(request)
    if denied is not None:
        return denied

    async with _semaphore:
        try:
            payload = await request.json()
        except Exception:
            return web.json_response({"ok": False, "message": "Некорректный JSON."}, status=400)
        if not isinstance(payload, dict):
            return web.json_response({"ok": False, "message": "Ожидается JSON-объект."}, status=400)

        target = get_ahelp_notify_target(payload.get("serverName"))
        if target is None:
            return web.json_response(
                {"ok": False, "message": "Сервер не распознан или AHELP_CHANNEL не настроен."},
                status=404,
            )

        server, channel_id, ping_role = target

        try:
            channel = await _resolve_notify_channel(channel_id)
        except Exception as error:
            print(f"[AHelpNotify] channel={channel_id} error={error}")
            return web.json_response({"ok": False, "message": "Канал недоступен."}, status=404)

        server_label = get_server_label(server, payload.get("serverName"))
        round_id = payload.get("roundId", "—")
        run_level = payload.get("runLevel")
        conversations = payload.get("conversations") or []
        if not isinstance(conversations, list):
            return web.json_response({"ok": False, "message": "Поле conversations должно быть списком."}, status=400)
        if len(conversations) > _AHELP_CONVERSATIONS_LIMIT:
            return web.json_response({"ok": False, "message": "Слишком много обращений в одном запросе."}, status=400)

        created = 0
        updated = 0
        for conversation in conversations:
            if not isinstance(conversation, dict):
                continue
            conversation_id = str(conversation.get("conversationId") or conversation.get("userId") or "")
            if not conversation_id:
                continue

            key = (server.get("name", "?"), conversation_id)
            transcript = str(conversation.get("transcript") or "")
            transcript_hash = hashlib.sha256(transcript.encode("utf-8")).digest()
            state = _ahelp_messages.get(key)
            embed = build_ahelp_embed(conversation, server_label, round_id, run_level)

            try:
                if state is None:
                    # Новое обращение: пинг роли вне embed, сам текст только в embed.
                    ping_content = build_role_ping_content(ping_role)
                    if ping_content is None:
                        message = await channel.send(embed=embed)
                    else:
                        message = await channel.send(content=ping_content, embed=embed)
                    if len(_ahelp_messages) >= _AHELP_STATE_LIMIT:
                        _ahelp_messages.pop(next(iter(_ahelp_messages)))
                    _ahelp_messages[key] = {"message_id": message.id, "transcript_hash": transcript_hash}
                    created += 1
                elif state.get("transcript_hash") != transcript_hash:
                    try:
                        message = await channel.fetch_message(state["message_id"])
                        await message.edit(embed=embed)
                    except disnake.HTTPException:
                        message = await channel.send(embed=embed)
                        state["message_id"] = message.id
                    state["transcript_hash"] = transcript_hash
                    updated += 1
            except Exception as error:
                print(f"[AHelpNotify] channel={channel_id} conversation={conversation_id} error={error}")
                return web.json_response({"ok": False, "message": "Не удалось отправить уведомление."}, status=502)

        return web.json_response({"ok": True, "message": "ok", "created": created, "updated": updated})


async def _ban_event_handler(request: web.Request) -> web.Response:
    denied = _check_bot_api_access(request)
    if denied is not None:
        return denied

    async with _semaphore:
        try:
            payload = await request.json()
        except Exception:
            return web.json_response({"ok": False, "message": "Некорректный JSON."}, status=400)
        if not isinstance(payload, dict):
            return web.json_response({"ok": False, "message": "Ожидается JSON-объект."}, status=400)

        if str(payload.get("type") or "") != "ban":
            return web.json_response({"ok": False, "message": "Неизвестный тип события."}, status=400)

        target = get_ban_notify_target(payload.get("serverName"))
        if target is None:
            return web.json_response(
                {"ok": False, "message": "Сервер не распознан или BAN_CHANNEL не настроен."},
                status=404,
            )

        server, channel_id = target

        try:
            channel = await _resolve_notify_channel(channel_id)
        except Exception as error:
            print(f"[BanNotify] channel={channel_id} error={error}")
            return web.json_response({"ok": False, "message": "Канал недоступен."}, status=404)

        embed = build_ban_embed(payload, get_server_label(server, payload.get("serverName")))

        try:
            await channel.send(embed=embed)
        except Exception as error:
            print(f"[BanNotify] channel={channel_id} send error={error}")
            return web.json_response({"ok": False, "message": "Не удалось отправить уведомление."}, status=502)

        return web.json_response({"ok": True, "message": "ok"})


async def ensure_bot_api_started() -> bool:
    global _api_runner, _api_site, _api_started

    if _api_started:
        return True

    if not (BOT_API_TOKEN or "").strip():
        print("[DiscordAuthApi] BOT_API_TOKEN не задан. API глобальной отвязки не запущен.")
        return False

    app = web.Application(client_max_size=256 * 1024)
    app.router.add_post("/api/v1/discord/unlink", _discord_unlink_handler)
    app.router.add_post("/api/v1/round/event", _round_event_handler)
    app.router.add_post("/api/v1/ahelp/event", _ahelp_event_handler)
    app.router.add_post("/api/v1/ban/event", _ban_event_handler)

    _api_runner = web.AppRunner(app)
    await _api_runner.setup()

    _api_site = web.TCPSite(_api_runner, BOT_API_HOST, BOT_API_PORT)
    await _api_site.start()

    _api_started = True
    print(f"[DiscordAuthApi] Started on http://{BOT_API_HOST}:{BOT_API_PORT}")
    return True
