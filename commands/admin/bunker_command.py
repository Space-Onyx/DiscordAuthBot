import aiohttp
from disnake.ext.commands import has_any_role

from bot_init import bot
from dataConfig import DEFAULT_SERVER_NAME, ROLE_ACCESS_DOWN_ADMIN, build_admin_headers, build_admin_url
from server_utils import resolve_server_for_command


@has_any_role(*ROLE_ACCESS_DOWN_ADMIN)
@bot.command(name="bunker")
async def bunker_command(ctx, switch: str, server: str = DEFAULT_SERVER_NAME):
    server_name, error = resolve_server_for_command(server)
    if error:
        await ctx.send(error)
        return

    if switch.lower() not in ["on", "off"]:
        await ctx.send("Используйте 'on' или 'off'.")
        return

    bunker_bool = switch.lower() == "on"
    status = "включен" if bunker_bool else "выключен"

    url = build_admin_url("/admin/actions/panic_bunker", server_name)
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

    data = {"game.panic_bunker.enabled": bunker_bool}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=data) as resp:
                if resp.status == 200:
                    await ctx.send(f"Паник-бункер {status}. Сервер: {server_name}.")
                else:
                    await ctx.send(f"Ошибка {resp.status}: {await resp.text()}")
    except Exception as e:
        await ctx.send(f"Ошибка: {e}")
