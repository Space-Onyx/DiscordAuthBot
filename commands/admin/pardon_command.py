from datetime import datetime

import pytz
from disnake.ext.commands import has_any_role

from bot_init import bot, ss14_db
from dataConfig import DEFAULT_DB_SERVER, ROLE_ACCESS_DEPARTAMENT_OF_UNBAN_ADMIN
from server_utils import resolve_server_for_command


@has_any_role(*ROLE_ACCESS_DEPARTAMENT_OF_UNBAN_ADMIN)
@bot.command(name="pardon")
async def pardon_command(ctx, ban_id: int, server: str = DEFAULT_DB_SERVER):
    server_name, error = resolve_server_for_command(server, db_required=True)
    if error:
        await ctx.send(error)
        return

    ds_id = str(ctx.author.id)

    admin_guid = await ss14_db.get_player_guid_by_discord_id(ds_id, server_name)
    if not admin_guid:
        await ctx.send("Ваш GUID не найден в БД. Сначала привяжите аккаунт Discord.")
        return

    time_ban = datetime.now(pytz.timezone("Europe/Moscow"))
    reply, message = await ss14_db.unban_player(ban_id, admin_guid, time_ban, server_name)

    if not reply:
        await ctx.send(message)
        return

    await ctx.send(message)
