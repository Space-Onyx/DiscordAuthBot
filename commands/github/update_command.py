import aiohttp
from disnake.ext.commands import has_any_role

from bot_init import bot
from dataConfig import (
    DEFAULT_SERVER_NAME,
    ROLE_ACCESS_HEADS,
    build_post_data,
    build_post_headers,
    build_update_url,
    get_server,
)
from server_utils import resolve_server_for_command


@has_any_role(*ROLE_ACCESS_HEADS)
@bot.command(name="update")
async def update_command(ctx, server: str = DEFAULT_SERVER_NAME):
    server_name, error = resolve_server_for_command(server)
    if error:
        await ctx.send(error)
        return

    server_config = get_server(server_name)
    if not server_config:
        await ctx.send("Не удалось получить конфиг сервера.")
        return

    url = build_update_url(server_name)
    data = build_post_data(server_name)
    headers = build_post_headers(server_name, data)

    if not url or data is None or headers is None:
        await ctx.send("Не удалось сформировать запрос обновления.")
        return

    await ctx.send(f"Запуск обновления {server_name.upper()}...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as resp:
                if resp.status == 200:
                    await ctx.send(f"Код {resp.status}. Обновление на {server_name.upper()} успешно отправлено.")
                else:
                    await ctx.send(f"Код {resp.status}. Обновление на {server_name.upper()} не отправлено.")
    except Exception as e:
        await ctx.send(f"Ошибка: {e}")
