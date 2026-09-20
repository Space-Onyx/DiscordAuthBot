import re

from disnake import Embed
from disnake.ext import commands

from bot_init import bot, ss14_db
from dataConfig import (
    DEFAULT_DB_SERVER,
    ROLE_ACCESS_EVENTOLOGY,
    ROLE_ACCESS_MODERATORS,
    ROLE_ACCESS_OBSERVER_ADMIN,
)
from server_utils import parse_server_from_tokens, resolve_server_for_command


DISCORD_MENTION = re.compile(r"^<@!?(\d+)>$")


def _has_admin_access(member) -> bool:
    permissions = getattr(member, "guild_permissions", None)
    if permissions and permissions.administrator:
        return True

    allowed_roles = {
        *ROLE_ACCESS_MODERATORS,
        *ROLE_ACCESS_EVENTOLOGY,
        *ROLE_ACCESS_OBSERVER_ADMIN,
    }
    return any(role.id in allowed_roles for role in getattr(member, "roles", ()))


def _format_playtime(seconds: float) -> str:
    total_minutes = max(0, int(seconds // 60))
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours} ч {minutes} мин"


def _split_lines(lines: list[str], limit: int = 3900) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    current_length = 0
    for line in lines:
        line_length = len(line) + 1
        if current and current_length + line_length > limit:
            chunks.append("\n".join(current))
            current = []
            current_length = 0
        current.append(line)
        current_length += line_length
    if current:
        chunks.append("\n".join(current))
    return chunks


@bot.command(name="playtime", aliases=["hours"])
@commands.cooldown(2, 20, commands.BucketType.user)
async def playtime_command(ctx, *args: str):
    tokens = list(args)
    if len(tokens) == 1:
        selected_server, error = resolve_server_for_command(tokens[0], db_required=True)
        if not error:
            tokens = []
            server_name = selected_server
        else:
            server_name = None
    else:
        tokens, server_name, error = parse_server_from_tokens(tokens, db_required=True)
        if error:
            await ctx.send(error)
            return

    if server_name is None:
        server_name, error = resolve_server_for_command(DEFAULT_DB_SERVER, db_required=True)
        if error:
            await ctx.send(error)
            return

    if len(tokens) > 1:
        await ctx.send("Использование: `&playtime [ник|@пользователь] [--server имя]`.")
        return

    target = tokens[0] if tokens else None
    is_admin = _has_admin_access(ctx.author)
    discord_id = str(ctx.author.id)
    nickname = None
    if target:
        mention = DISCORD_MENTION.fullmatch(target)
        target_discord_id = mention.group(1) if mention else target if target.isdigit() else None
        is_self = target_discord_id == discord_id
        if not is_self and not is_admin:
            await ctx.send("Чужую наигровку могут смотреть только администраторы.")
            return

        if target_discord_id:
            discord_id = target_discord_id
        else:
            discord_id = None
            nickname = target

    try:
        playtimes = await ss14_db.get_player_playtime(
            server_name,
            discord_id=discord_id,
            nickname=nickname,
        )
    except Exception as error:
        print(f"[Playtime] server={server_name} user={ctx.author.id} error={error}")
        await ctx.send("Не удалось получить наигровку. Попробуйте позже.")
        return

    if not playtimes:
        message = "Игрок не найден." if nickname else "Аккаунт Discord не привязан к игроку на этом сервере."
        await ctx.send(message)
        return

    player_name = playtimes[0]["last_seen_user_name"]
    tracker_lines = [
        f"`{row['tracker']}`: **{_format_playtime(row['seconds'])}**"
        for row in playtimes
        if row["tracker"] and row["tracker"] != "Overall"
    ]
    overall = next((row for row in playtimes if row["tracker"] == "Overall"), None)
    total_text = _format_playtime(overall["seconds"]) if overall else "нет данных"
    descriptions = _split_lines(tracker_lines) if tracker_lines else ["Нет наигровки по ролям."]

    embeds = []
    for index, description in enumerate(descriptions):
        title = f"Наигранное время: {player_name}"
        if len(descriptions) > 1:
            title += f" ({index + 1}/{len(descriptions)})"
        embed = Embed(title=title, description=description, color=0x3498DB)
        if index == 0:
            embed.add_field(name="Общее время", value=total_text, inline=False)
        embed.set_footer(text=f"Сервер: {server_name.upper()} | Роли указаны по tracker ID")
        embeds.append(embed)

    for embed in embeds:
        await ctx.send(embed=embed)
