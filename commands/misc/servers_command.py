from disnake import Embed

from bot_init import bot
from dataConfig import get_db_server_names, get_server_names


@bot.command(name="servers")
async def servers_command(ctx):
    server_names = get_server_names()
    if not server_names:
        await ctx.send("Серверы не настроены.")
        return

    db_servers = set(get_db_server_names())
    embed = Embed(title="Список серверов", color=0x3498DB)
    for name in server_names:
        value = "Статус и наигровка" if name in db_servers else "Только статус"
        embed.add_field(name=name.upper(), value=value, inline=False)

    await ctx.send(embed=embed)
