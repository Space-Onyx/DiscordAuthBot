import disnake
from disnake.ext.commands import has_any_role

from bot_init import bot, ss14_db
from dataConfig import ROLE_ACCESS_MODERATORS, ROLE_ACCESS_EVENTOLOGY, get_db_server_names
from template_embed import COLOR_DANGER, COLOR_WARNING


@has_any_role(*ROLE_ACCESS_MODERATORS, *ROLE_ACCESS_EVENTOLOGY)
@bot.command(name="admin")
async def admin_command(ctx, nickname: str):
    db_servers = get_db_server_names()
    if not db_servers:
        await ctx.send("В боте не настроены серверы с БД.")
        return

    found = []
    for server_name in db_servers:
        info = await ss14_db.get_admin_permission(nickname, server_name)
        if info:
            found.append((server_name, info))

    if not found:
        embed = disnake.Embed(
            title="Права не найдены",
            description=f"`{nickname}` не имеет административных прав.",
            color=COLOR_DANGER,
        )
        await ctx.send(embed=embed)
        return

    embed = disnake.Embed(title=f"Администратор · {nickname}"[:256], color=COLOR_WARNING)
    for server_name, info in found:
        embed.add_field(
            name=server_name.upper(),
            value=f"{info[0]}\n`{info[1]}`",
            inline=True,
        )

    await ctx.send(embed=embed)
