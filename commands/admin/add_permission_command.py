from disnake.ext.commands import has_any_role

from bot_init import bot, ss14_db
from dataConfig import DEFAULT_DB_SERVER, LOG_CHANNEL_ID, MY_DS_ID, ROLE_ACCESS_HEADS
from server_utils import resolve_server_for_command


@has_any_role(*ROLE_ACCESS_HEADS)
@bot.command(name="add_permission")
async def add_permission_command(ctx, username: str, title: str, permission: str, server: str = DEFAULT_DB_SERVER):
    server_name, error = resolve_server_for_command(server, db_required=True)
    if error:
        await ctx.send(error)
        return

    if await ss14_db.get_admin_permission(username, db_name=server_name):
        await ctx.send(f"Пользователь {username} уже имеет права на {server_name.upper()}.")
        return

    guid = await ss14_db.get_player_guid(username, server_name)
    if not guid:
        await ctx.send(f"Пользователь {username} не найден в БД {server_name.upper()}.")
        return

    answer, message = await ss14_db.add_permission_admin(guid, username, title, permission, server_name)
    if not answer:
        await ctx.send(f"Ошибка: {message}")
        return

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"<@{MY_DS_ID}>")

    await ctx.send(message)
