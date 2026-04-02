import aiohttp
from disnake.ext import tasks

from bot_init import bot
from dataConfig import build_status_url, get_status_message_targets, resolve_server_name
from status_utils import build_status_embed, compute_round_length_text, compute_status_text


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
            if not url:
                embed = build_status_embed({}, resolved_server or "не задан", "Неизвестно", "Не начался")
                embed.title = "Ошибка"
                embed.description = "Не настроен сервер для статус-сообщения."
            else:
                try:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            status_text = compute_status_text(data.get("run_level"))
                            round_length_text = compute_round_length_text(data.get("round_start_time"))
                            embed = build_status_embed(data, resolved_server or "не задан", status_text, round_length_text)
                        else:
                            embed = build_status_embed({}, resolved_server or "не задан", "Неизвестно", "Не начался")
                            embed.title = "Ошибка"
                            embed.description = f"Код {resp.status}"
                except Exception as e:
                    embed = build_status_embed({}, resolved_server or "не задан", "Неизвестно", "Не начался")
                    embed.title = "Ошибка"
                    embed.description = str(e)

            pinned = []
            async for msg in channel.pins():
                pinned.append(msg)

            footer_text = f"Сервер: {resolved_server or 'не задан'}"
            old_message = next(
                (
                    m for m in pinned
                    if m.author == channel.guild.me
                    and m.embeds
                    and m.embeds[0].footer
                    and m.embeds[0].footer.text == footer_text
                ),
                None,
            )

            if old_message:
                await old_message.edit(embed=embed)
            else:
                new_message = await channel.send(embed=embed)
                await new_message.pin()
