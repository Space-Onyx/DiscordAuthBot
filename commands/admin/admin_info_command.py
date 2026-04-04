import aiohttp
from disnake import Embed
from disnake.ext.commands import has_any_role

from bot_init import bot
from dataConfig import DEFAULT_SERVER_NAME, ROLE_ACCESS_MODERATORS, ROLE_ACCESS_EVENTOLOGY, build_admin_headers, build_admin_url
from server_utils import resolve_server_for_command
from template_embed import embed_admin_info


def add_chunked_fields(embed, name, value, max_length=1024, inline=False):
    """Разбивает длинное значение на несколько полей."""
    if len(value) <= max_length:
        embed.add_field(name=name, value=value, inline=inline)
        return

    chunks, chunk = [], ""
    lines = value.split("\n")
    for line in lines:
        if len(chunk) + len(line) + 1 > max_length:
            chunks.append(chunk.strip())
            chunk = line
        else:
            chunk += f"\n{line}" if chunk else line

    if chunk:
        chunks.append(chunk.strip())

    for i, value_chunk in enumerate(chunks):
        field_name = name if i == 0 else f"{name} (часть {i + 1})"
        embed.add_field(name=field_name, value=value_chunk, inline=inline)


@has_any_role(*ROLE_ACCESS_MODERATORS, *ROLE_ACCESS_EVENTOLOGY)
@bot.command(name="admin_info")
async def admin_info_command(ctx, server: str = DEFAULT_SERVER_NAME):
    server_name, error = resolve_server_for_command(server)
    if error:
        await ctx.send(error)
        return

    url = build_admin_url("/admin/info", server_name)
    if not url:
        await ctx.send("Не удалось сформировать URL admin API.")
        return

    headers = build_admin_headers(server_name)
    if headers is None:
        await ctx.send(
            f"Не настроен ADMIN API токен для сервера {server_name.upper()}. "
            f"Укажите SERVER_*_ADMIN_API_TOKEN или глобальный ADMIN_API."
        )
        return

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    await ctx.send(f"Ошибка: код {resp.status}")
                    return

                data = await resp.json()
                embed = Embed(title=embed_admin_info["title"], color=embed_admin_info["color"])
                for field in embed_admin_info["fields"]:
                    try:
                        value = eval(field["value"])
                        if field["name"] in ["Игроки", "Деадмины", "Правила игры"]:
                            add_chunked_fields(embed, field["name"], value, inline=field["inline"])
                        else:
                            embed.add_field(name=field["name"], value=value, inline=field["inline"])
                    except Exception:
                        embed.add_field(name=field["name"], value="Ошибка", inline=field["inline"])

                embed.set_footer(text=f"Сервер: {server_name}")
                await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Ошибка: {e}")
