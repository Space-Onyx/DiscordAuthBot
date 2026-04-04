import disnake
from disnake.ext.commands import has_any_role

from bot_init import bot, ss14_db
from dataConfig import ROLE_ACCESS_MODERATORS, ROLE_ACCESS_EVENTOLOGY, get_db_server_names


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
            title="Админ не найден",
            description=f"{nickname} не имеет админ-прав на настроенных серверах.",
            color=0xFF0000,
        )
        await ctx.send(embed=embed)
        return

    embed = disnake.Embed(title=f"Информация о {nickname}", color=0xFFD700)
    for server_name, info in found:
        embed.add_field(
            name=server_name.upper(),
            value=f"**Титул:** {info[0]}\n**Ранг:** {info[1]}",
            inline=False,
        )

    await ctx.send(embed=embed)
