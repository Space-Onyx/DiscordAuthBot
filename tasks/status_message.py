import json
import os
import time

import aiohttp
import disnake
from disnake.ext import tasks

from bot_init import bot
from dataConfig import build_status_url, get_status_message_targets, resolve_server_name
from status_utils import build_status_embed, compute_round_length_text, compute_status_text
from template_embed import embed_status

_STATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "status_message_state.json")
_STATUS_FOOTER_PREFIX = "Сервер: "
_STATUS_FIELD_NAME = next(
    (field["name"] for field in embed_status["fields"] if field.get("key") == "status"),
    "Статус",
)
_SKIP = object()

_status_message_ids: dict[int, int] = {}
_status_lookup_error_last: dict[int, float] = {}


def _load_state() -> dict[int, int]:
    try:
        with open(_STATE_PATH, "r", encoding="utf-8") as file:
            raw = json.load(file)
        return {int(channel_id): int(message_id) for channel_id, message_id in raw.items()}
    except (OSError, ValueError, TypeError):
        return {}


def _save_state() -> None:
    try:
        with open(_STATE_PATH, "w", encoding="utf-8") as file:
            json.dump(
                {str(channel_id): message_id for channel_id, message_id in _status_message_ids.items()},
                file,
                indent=2,
            )
    except OSError as e:
        print(f"[StatusMessage] Failed to persist state: {e}")


_status_message_ids = _load_state()


def _log_lookup_error_once(channel_id: int, text: str) -> None:
    now = time.monotonic()
    if now - _status_lookup_error_last.get(channel_id, 0.0) > 600:
        _status_lookup_error_last[channel_id] = now
        print(text)


def _is_status_message(message) -> bool:
    if bot.user is None or message.author.id != bot.user.id or not message.embeds:
        return False
    embed = message.embeds[0]
    footer = embed.footer
    if not footer or not footer.text or not footer.text.startswith(_STATUS_FOOTER_PREFIX):
        return False
    return any(field.name == _STATUS_FIELD_NAME for field in embed.fields)


async def _resolve_status_message(channel, channel_id: int):
    cached_id = _status_message_ids.get(channel_id)
    if cached_id is not None:
        try:
            message = await channel.fetch_message(cached_id)
            if _is_status_message(message):
                return message
        except disnake.NotFound:
            pass
        except disnake.HTTPException:
            _log_lookup_error_once(channel_id, f"[StatusMessage] message lookup unavailable for channel {channel_id}, skipping update")
            return _SKIP
        _status_message_ids.pop(channel_id, None)
        _save_state()

    try:
        pinned = [message async for message in channel.pins()]
    except disnake.HTTPException:
        _log_lookup_error_once(channel_id, f"[StatusMessage] pins unavailable for channel {channel_id}, skipping update")
        return _SKIP

    candidates = [message for message in pinned if _is_status_message(message)]
    if not candidates:
        return None

    keep = min(candidates, key=lambda message: message.created_at)
    for extra in candidates:
        if extra.id == keep.id:
            continue
        try:
            await extra.delete()
        except disnake.HTTPException:
            pass
    return keep


@tasks.loop(minutes=2)
async def status_update():
    targets = get_status_message_targets()
    if not targets:
        return

    async with aiohttp.ClientSession() as session:
        for server_name, channel_id in targets:
            channel = bot.get_channel(channel_id)
            if not channel:
                try:
                    channel = await bot.fetch_channel(channel_id)
                except Exception:
                    continue

            resolved_server = resolve_server_name(server_name)
            url = build_status_url(resolved_server)
            host_label = resolved_server or "не задан"
            if not url:
                embed = build_status_embed({}, host_label, "Неизвестно", "Не начался")
                embed.title = "Ошибка"
                embed.description = "Не настроен сервер для статус-сообщения."
            else:
                try:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            host_label = (data.get("name") or "").strip() or host_label
                            status_text = compute_status_text(data.get("run_level"))
                            round_length_text = compute_round_length_text(data.get("round_start_time"))
                            embed = build_status_embed(data, host_label, status_text, round_length_text)
                        else:
                            embed = build_status_embed({}, host_label, "Неизвестно", "Не начался")
                            embed.title = "Ошибка"
                            embed.description = f"Код {resp.status}"
                except Exception as e:
                    print(f"[StatusMessage] server={server_name} error={e}")
                    embed = build_status_embed({}, host_label, "Неизвестно", "Не начался")
                    embed.title = "Ошибка"
                    embed.description = "Сервер статуса недоступен."

            old_message = await _resolve_status_message(channel, channel_id)
            if old_message is _SKIP:
                continue

            try:
                if old_message is not None:
                    await old_message.edit(embed=embed)
                    if _status_message_ids.get(channel_id) != old_message.id:
                        _status_message_ids[channel_id] = old_message.id
                        _save_state()
                else:
                    new_message = await channel.send(embed=embed)
                    _status_message_ids[channel_id] = new_message.id
                    _save_state()
                    try:
                        await new_message.pin()
                    except disnake.HTTPException:
                        pass
            except disnake.HTTPException:
                print(f"[StatusMessage] Failed to update status message in channel {channel.id}")
