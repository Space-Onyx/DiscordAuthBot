from disnake import Embed

from bot_init import bot
from dataConfig import get_db_server_names, get_server_names
from template_embed import COLOR_PRIMARY


@bot.command(name="servers")
async def servers_command(ctx):
    server_names = get_server_names()
    if not server_names:
        await ctx.send("Серверы не настроены.")
        return

    db_servers = set(get_db_server_names())
    embed = Embed(title="Игровые серверы", color=COLOR_PRIMARY)
    for name in server_names:
        value = "Статус · Наигровка" if name in db_servers else "Статус"
        embed.add_field(name=name.upper(), value=value, inline=True)

    await ctx.send(embed=embed)
