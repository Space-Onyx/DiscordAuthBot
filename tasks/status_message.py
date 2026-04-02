import aiohttp
from disnake import Embed
from disnake.ext import tasks

from bot_init import bot
from dataConfig import build_status_url, get_status_message_targets, resolve_server_name
from template_embed import embed_status


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
                embed = Embed(title="Ошибка", description="Не настроен сервер для статус-сообщения.", color=0xFF0000)
            else:
                try:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            run_level = data.get("run_level")
                            if run_level == 1:
                                status_text = "Раунд идет"
                            elif run_level == 0:
                                status_text = "Ожидание"
                            else:
                                status_text = "Неизвестно"

                            title_value = embed_status["title"]
                            try:
                                title_value = eval(title_value)
                            except Exception:
                                title_value = str(title_value)

                            embed = Embed(title=title_value, color=embed_status["color"])
                            if "description" in embed_status:
                                embed.description = eval(embed_status["description"])
                            for field in embed_status["fields"]:
                                embed.add_field(
                                    name=field["name"],
                                    value=eval(field["value"]),
                                    inline=field["inline"],
                                )
                            embed.set_footer(text=f"Сервер: {resolved_server or 'не задан'}")
                        else:
                            embed = Embed(title="Ошибка", description=f"Код {resp.status}", color=0xFF0000)
                except Exception as e:
                    embed = Embed(title="Ошибка", description=str(e), color=0xFF0000)

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
