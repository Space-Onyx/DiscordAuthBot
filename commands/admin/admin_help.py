from bot_init import bot
from dataConfig import (
    ROLE_ACCESS_DEPARTAMENT_OF_UNBAN_ADMIN,
    ROLE_ACCESS_DOWN_ADMIN,
    ROLE_ACCESS_EVENTOLOGY,
    ROLE_ACCESS_HEADS,
    ROLE_ACCESS_MODERATORS,
    ROLE_ACCESS_OBSERVER_ADMIN,
    ROLE_ACCESS_TOP_HEADS,
)
from template_embed import embed_admin_help
from disnake import Embed
from disnake.ext.commands import has_any_role

@has_any_role(
    *ROLE_ACCESS_HEADS,
    *ROLE_ACCESS_MODERATORS,
    *ROLE_ACCESS_EVENTOLOGY,
    *ROLE_ACCESS_DOWN_ADMIN,
    *ROLE_ACCESS_OBSERVER_ADMIN,
    *ROLE_ACCESS_DEPARTAMENT_OF_UNBAN_ADMIN,
    *ROLE_ACCESS_TOP_HEADS,
)
@bot.command(name="admin_help")
async def admin_help_command(ctx):
    embed = Embed(title=embed_admin_help["title"], color=embed_admin_help["color"], description=embed_admin_help["description"])
    for field in embed_admin_help["fields"]:
        embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])
    if bot.user is not None:
        embed.set_author(name=f"{bot.user.display_name} · Администрирование", icon_url=bot.user.display_avatar.url)
    await ctx.send(embed=embed)
