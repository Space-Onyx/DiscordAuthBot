import aiohttp
from disnake.ext.commands import has_any_role

from bot_init import bot, ss14_db
from dataConfig import DEFAULT_SERVER_NAME, ROLE_ACCESS_MODERATORS, build_admin_headers, build_admin_url
from server_utils import resolve_server_for_command


@has_any_role(*ROLE_ACCESS_MODERATORS)
@bot.command(name="ban")
async def ban_command(ctx, nickname: str, reason: str, time: str, server: str = DEFAULT_SERVER_NAME):
    server_name, error = resolve_server_for_command(server)
    if error:
        await ctx.send(error)
        return

    discord_id = str(ctx.author.id)

    admin_guid = await ss14_db.get_player_guid_by_discord_id(discord_id, server_name)
    if not admin_guid:
        await ctx.send("⚠️ Ваш GUID не найден в БД. Сначала привяжите аккаунт Discord.")
        return

    admin_name = await ss14_db.get_admin_name(admin_guid, server_name)
    if not admin_name:
        await ctx.send("⚠️ Ваш аккаунт SS14 не найден в БД выбранного сервера.")
        return

    player_guid = await ss14_db.get_player_guid(nickname, server_name)
    if not player_guid:
        await ctx.send("❌ Игрок не найден в БД выбранного сервера.")
        return

    if not str(time).strip():
        await ctx.send("Ошибка: время бана не может быть пустым.")
        return

    url = build_admin_url("/admin/actions/server_ban", server_name)
    if not url:
        await ctx.send("Не удалось сформировать URL admin API.")
        return

    post_data = {"NickName": nickname, "Reason": reason, "Time": time}
    actor_data = {"Guid": str(admin_guid), "Name": admin_name}

    headers = build_admin_headers(server_name, actor_data)
    if headers is None:
        await ctx.send(
            f"Не настроен ADMIN API токен для сервера {server_name.upper()}. "
            f"Укажите SERVER_*_ADMIN_API_TOKEN или глобальный ADMIN_API."
        )
        return

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=post_data) as resp:
                if resp.status == 200:
                    await ctx.send(
                        f"✅ Игрок {nickname} забанен на {time} минут. Причина: {reason}. Сервер: {server_name}."
                    )
                else:
                    await ctx.send(f"Ошибка: код {resp.status}")
    except Exception as e:
        await ctx.send(f"Ошибка: {e}")
