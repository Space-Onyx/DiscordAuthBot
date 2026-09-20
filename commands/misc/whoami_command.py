from disnake import Embed
from disnake.ext import commands

from bot_init import bot, ss14_db
from dataConfig import get_db_server_names
from template_embed import COLOR_PRIMARY, COLOR_WARNING


def _format_hours(seconds: float) -> str:
    hours, minutes = divmod(max(0, int(seconds // 60)), 60)
    return f"{hours} ч {minutes} мин"


def _format_tracker(tracker: str) -> str:
    return tracker[3:] if tracker.casefold().startswith("job") and len(tracker) > 3 else tracker


@bot.command(name="whoami", aliases=["account"])
@commands.cooldown(2, 30, commands.BucketType.user)
async def whoami_command(ctx):
    servers = get_db_server_names()
    if not servers:
        await ctx.send("Серверы с БД не настроены.")
        return

    embed = Embed(
        title=f"Профиль · {ctx.author.display_name}"[:256],
        description=f"<@{ctx.author.id}> · `{ctx.author.id}`",
        color=COLOR_PRIMARY,
    )
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    linked_count = 0
    total_seconds = 0.0
    for server_name in servers:
        try:
            playtimes = await ss14_db.get_player_playtime(server_name, discord_id=str(ctx.author.id))
        except Exception as error:
            print(f"[WhoAmI] server={server_name} user={ctx.author.id} error={error}")
            embed.add_field(name=server_name.upper(), value="БД недоступна", inline=False)
            continue

        if not playtimes:
            embed.add_field(name=server_name.upper(), value="Аккаунт не привязан", inline=False)
            continue

        linked_count += 1
        overall = next((row for row in playtimes if row["tracker"] == "Overall"), None)
        server_seconds = float(overall["seconds"]) if overall else 0.0
        total_seconds += server_seconds
        roles = [row for row in playtimes if row["tracker"] and row["tracker"] != "Overall"][:3]
        role_text = "\n".join(
            f"`{_format_tracker(row['tracker'])}` · {_format_hours(row['seconds'])}"
            for row in roles
        ) or "Нет данных по должностям"
        embed.add_field(
            name=server_name.upper(),
            value=(
                f"Игрок: `{playtimes[0]['last_seen_user_name']}`\n"
                f"Всего: **{_format_hours(server_seconds)}**\n"
                f"\n{role_text}"
            ),
            inline=False,
        )

    if linked_count:
        embed.add_field(
            name="Сводка",
            value=f"Серверов: **{linked_count}/{len(servers)}**\nОбщая наигровка: **{_format_hours(total_seconds)}**",
            inline=False,
        )
    else:
        embed.color = COLOR_WARNING
        embed.add_field(name="Привязка", value="Нет привязанных аккаунтов.", inline=False)
    await ctx.send(embed=embed)
