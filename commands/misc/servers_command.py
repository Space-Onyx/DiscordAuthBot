from disnake import Embed

from bot_init import bot
from dataConfig import SERVERS, get_db_server_names, get_server_names


@bot.command(name="servers")
async def servers_command(ctx):
    server_names = get_server_names()
    if not server_names:
        await ctx.send("Серверы не настроены.")
        return

    db_servers = set(get_db_server_names())

    embed = Embed(title="Список серверов", color=0x3498DB)
    for name in server_names:
        server = SERVERS[name]
        db_status = "Да" if name in db_servers else "Нет"
        value = (
            f"Адрес: `{server['address']}`\n"
            f"Status порт: `{server['status_port']}`\n"
            f"Admin API порт: `{server['admin_api_port']}`\n"
            f"POST порт: `{server['post_port']}`\n"
            f"БД настроена: `{db_status}`"
        )
        embed.add_field(name=name.upper(), value=value, inline=False)

    await ctx.send(embed=embed)
