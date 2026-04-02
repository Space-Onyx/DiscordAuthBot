from disnake import Embed
from disnake.ext.commands import has_any_role

from bot_init import bot, ss14_db
from dataConfig import DEFAULT_DB_SERVER, ROLE_ACCESS_HEADS
from server_utils import resolve_server_for_command
from template_embed import embed_list_permission


@bot.command(name="list_permission")
@has_any_role(*ROLE_ACCESS_HEADS)
async def list_permission_command(ctx, dbname: str = DEFAULT_DB_SERVER):
    server_name, error = resolve_server_for_command(dbname, db_required=True)
    if error:
        await ctx.send(error)
        return

    list_permissions = await ss14_db.get_list_permission(server_name)

    embed = Embed(title=embed_list_permission["title"], color=embed_list_permission["color"])
    embed.description = f"Сервер: {server_name}"
    for row in list_permissions:
        embed.add_field(name="", value=f"`{row['name']}`", inline=False)

    await ctx.send(embed=embed)
