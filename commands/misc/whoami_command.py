from disnake import Embed
from disnake.ext import commands

from bot_init import bot, ss14_db
from dataConfig import get_db_server_names
from template_embed import COLOR_PRIMARY


def _format_hours(seconds: float) -> str:
    hours, minutes = divmod(max(0, int(seconds // 60)), 60)
    return f"{hours} ч {minutes} мин"


@bot.command(name="whoami", aliases=["account"])
@commands.cooldown(2, 30, commands.BucketType.user)
async def whoami_command(ctx):
    servers = get_db_server_names()
    if not servers:
        await ctx.send("Серверы с БД не настроены.")
        return

    embed = Embed(title="Ваш профиль SS14", color=COLOR_PRIMARY)
    found = False
    for server_name in servers:
        try:
            playtimes = await ss14_db.get_player_playtime(server_name, discord_id=str(ctx.author.id))
        except Exception as error:
            print(f"[WhoAmI] server={server_name} user={ctx.author.id} error={error}")
            embed.add_field(name=server_name.upper(), value="БД недоступна", inline=True)
            continue

        if not playtimes:
            embed.add_field(name=server_name.upper(), value="Не привязан", inline=True)
            continue

        found = True
        overall = next((row for row in playtimes if row["tracker"] == "Overall"), None)
        total = _format_hours(overall["seconds"]) if overall else "нет данных"
        embed.add_field(
            name=server_name.upper(),
            value=f"`{playtimes[0]['last_seen_user_name']}`\n**{total}**",
            inline=True,
        )

    if not found:
        embed.description = "Discord не привязан ни к одному настроенному серверу."
    await ctx.send(embed=embed)
