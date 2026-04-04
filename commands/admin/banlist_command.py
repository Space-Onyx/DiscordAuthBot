import disnake
from disnake.ext.commands import has_any_role

from bot_init import bot, ss14_db
from dataConfig import DEFAULT_DB_SERVER, ROLE_ACCESS_MODERATORS, ROLE_ACCESS_EVENTOLOGY
from server_utils import resolve_server_for_command


@has_any_role(*ROLE_ACCESS_MODERATORS, *ROLE_ACCESS_EVENTOLOGY)
@bot.command(name="banlist")
async def banlist_command(ctx, nickname: str, server: str = DEFAULT_DB_SERVER):
    server_name, error = resolve_server_for_command(server, db_required=True)
    if error:
        await ctx.send(error)
        return

    bans = await ss14_db.search_ban_player(nickname, server_name)

    if not bans:
        embed = disnake.Embed(
            title="Баны не найдены",
            description=f"{nickname} без банов на {server_name.upper()}.",
            color=0xFF0000,
        )
        await ctx.send(embed=embed)
        return

    embed = disnake.Embed(title=f"Баны {nickname} ({len(bans)})", color=0xFF8C00)
    embed.description = f"Сервер: {server_name.upper()}"

    for ban in bans:
        ban_id, ban_time, exp_time, reason, admin_name, unban_time, unban_admin = ban

        ban_time_str = ban_time.strftime("%Y-%m-%d %H:%M:%S") if ban_time else "?"
        exp_str = exp_time.strftime("%Y-%m-%d %H:%M:%S") if exp_time else "Постоянно"
        info = (
            f"**Дата:** {ban_time_str}\n"
            f"**Истекает:** {exp_str}\n"
            f"**Причина:** {reason}\n"
            f"**Админ:** {admin_name or '?'}"
        )

        if unban_time:
            unban_str = unban_time.strftime("%Y-%m-%d %H:%M:%S")
            info += f"\n**Разбан:** {unban_str} ({unban_admin or '?'})"

        embed.add_field(name=f"---------------\nБан #{ban_id}", value=info, inline=False)

    await ctx.send(embed=embed)
