import disnake
from disnake.ext.commands import has_any_role

from bot_init import bot, ss14_db
from dataConfig import DEFAULT_DB_SERVER, ROLE_ACCESS_MODERATORS, ROLE_ACCESS_EVENTOLOGY
from server_utils import resolve_server_for_command
from template_embed import COLOR_DANGER, COLOR_WARNING


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
            description=f"У `{nickname}` нет банов на `{server_name.upper()}`.",
            color=COLOR_DANGER,
        )
        await ctx.send(embed=embed)
        return

    embeds = []
    for index, ban in enumerate(bans):
        if index % 10 == 0:
            embed = disnake.Embed(
                title=f"Баны · {nickname} · {server_name.upper()}"[:256],
                description=f"Записей: **{len(bans)}**",
                color=COLOR_WARNING,
            )
            embeds.append(embed)
        ban_id, ban_time, exp_time, reason, admin_name, unban_time, unban_admin = ban

        ban_time_str = ban_time.strftime("%Y-%m-%d %H:%M:%S") if ban_time else "?"
        exp_str = exp_time.strftime("%Y-%m-%d %H:%M:%S") if exp_time else "Постоянно"
        info = (
            f"{reason}\n"
            f"`{ban_time_str}` → `{exp_str}`\n"
            f"Выдал: {admin_name or 'неизвестно'}"
        )

        if unban_time:
            unban_str = unban_time.strftime("%Y-%m-%d %H:%M:%S")
            info += f"\nСнят: `{unban_str}` · {unban_admin or 'неизвестно'}"

        embed.add_field(name=f"#{ban_id}", value=info[:1024], inline=False)

    for embed in embeds:
        await ctx.send(embed=embed)
