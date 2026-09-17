import aiohttp
import disnake
import time
from disnake.ext import tasks

from bot_init import bot
from dataConfig import build_status_url, get_status_message_targets, resolve_server_name
from status_utils import build_status_embed, compute_round_length_text, compute_status_text

_status_message_ids: dict[int, int] = {}
_status_lookup_error_last: dict[int, float] = {}


def _log_lookup_error_once(channel_id: int, text: str) -> None:
    now = time.monotonic()
    if now - _status_lookup_error_last.get(channel_id, 0.0) > 600:
        _status_lookup_error_last[channel_id] = now
        print(text)


def _is_status_message(message, footer_text: str, channel) -> bool:
    return (
        message.author == channel.guild.me
        and message.embeds
        and message.embeds[0].footer
        and message.embeds[0].footer.text == footer_text
    )


async def _get_pinned_messages(channel):
    try:
        return [msg async for msg in channel.pins()]
    except disnake.HTTPException:
        _log_lookup_error_once(channel.id, f"[StatusMessage] pins unavailable for channel {channel.id}, using history fallback")
        return None


async def _find_status_message(channel, channel_id: int, footer_text: str):
    cached = _status_message_ids.get(channel_id)
    if cached is not None:
        try:
            message = await channel.fetch_message(cached)
            if _is_status_message(message, footer_text, channel):
                return message, True
        except disnake.HTTPException:
            pass
        _status_message_ids.pop(channel_id, None)

    pinned = await _get_pinned_messages(channel)
    if pinned is not None:
        for message in pinned:
            if _is_status_message(message, footer_text, channel):
                return message, True

    try:
        async for message in channel.history(limit=50):
            if _is_status_message(message, footer_text, channel):
                return message, True
    except disnake.HTTPException:
        _log_lookup_error_once(channel_id, f"[StatusMessage] history unavailable for channel {channel_id}, skipping update")
        return None, False
    return None, True


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
                    embed = build_status_embed({}, host_label, "Неизвестно", "Не начался")
                    embed.title = "Ошибка"
                    embed.description = str(e)

            footer_text = (embed.footer.text if embed.footer else f"Сервер: {host_label}")
            old_message, looked_up = await _find_status_message(channel, channel_id, footer_text)
            if old_message is None and not looked_up:
                continue

            try:
                if old_message:
                    await old_message.edit(embed=embed)
                    _status_message_ids[channel_id] = old_message.id
                else:
                    new_message = await channel.send(embed=embed)
                    _status_message_ids[channel_id] = new_message.id
                    try:
                        await new_message.pin()
                    except disnake.HTTPException:
                        pass
            except disnake.HTTPException:
                print(f"[StatusMessage] Failed to update status message in channel {channel.id}")
