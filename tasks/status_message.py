import aiohttp
from disnake import Embed
from disnake.ext import tasks

from bot_init import bot
from dataConfig import CHANNEL_STATUS_MESSAGE, STATUS_MESSAGE_SERVER_NAME, build_status_url, resolve_server_name
from template_embed import embed_status


@tasks.loop(minutes=2)
async def status_update():
    channel = bot.get_channel(CHANNEL_STATUS_MESSAGE)
    if not channel:
        return

    resolved_server = resolve_server_name(STATUS_MESSAGE_SERVER_NAME)
    url = build_status_url(resolved_server)
    if not url:
        embed = Embed(title="Ошибка", description="Не настроен сервер для статус-сообщения.", color=0xFF0000)
    else:
        try:
            async with aiohttp.ClientSession() as session:
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
                            embed.add_field(name=field["name"], value=eval(field["value"]), inline=field["inline"])
                        embed.set_footer(text=f"Сервер: {resolved_server or 'не задан'}")
                    else:
                        embed = Embed(title="Ошибка", description=f"Код {resp.status}", color=0xFF0000)
        except Exception as e:
            embed = Embed(title="Ошибка", description=str(e), color=0xFF0000)

    pinned = []
    async for msg in channel.pins():
        pinned.append(msg)

    old_message = next((m for m in pinned if m.author == channel.guild.me), None)

    if old_message:
        await old_message.edit(embed=embed)
    else:
        new_message = await channel.send(embed=embed)
        await new_message.pin()
