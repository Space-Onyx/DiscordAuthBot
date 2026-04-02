import aiohttp
from disnake.ext.commands import has_any_role

from bot_init import bot
from dataConfig import (
    DEFAULT_SERVER_NAME,
    ROLE_ACCESS_HEADS,
    build_post_data,
    build_post_headers,
    build_restart_url,
)
from server_utils import resolve_server_for_command


@has_any_role(*ROLE_ACCESS_HEADS)
@bot.command(name="restart")
async def restart_command(ctx, server: str = DEFAULT_SERVER_NAME):
    server_name, error = resolve_server_for_command(server)
    if error:
        await ctx.send(error)
        return

    url = build_restart_url(server_name)
    data = build_post_data(server_name)
    headers = build_post_headers(server_name, data)

    if not url or data is None or headers is None:
        await ctx.send("Не удалось сформировать запрос рестарта.")
        return

    await ctx.send(f"Запущен рестарт {server_name.upper()} сервера...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers) as resp:
                if resp.status == 200:
                    await ctx.send(f"✅ Рестарт {server_name.upper()} выполнен.")
                else:
                    await ctx.send(f"Ошибка: код {resp.status}")
    except Exception as e:
        await ctx.send(f"Ошибка: {e}")
