from datetime import datetime

import aiohttp
import disnake
from disnake.ext.commands import has_any_role

from bot_init import bot, ss14_db
from dataConfig import CHECK_NICK_ACCOUNT_WHITELIST, DEFAULT_DB_SERVER, ROLE_ACCESS_MODERATORS
from server_utils import resolve_server_for_command
from template_embed import COLOR_DANGER


async def get_creation_date(uuid: str):
    url = f"https://auth.spacestation14.com/api/query/userid?userid={uuid}"
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    player_date = data.get("createdTime", None)
                    if player_date:
                        date_obj = datetime.fromisoformat(player_date)
                        unix = int(date_obj.timestamp())
                        return f"<t:{unix}:f>"
                    return "Дата не найдена"
                return f"Auth API: {resp.status}"
    except Exception as error:
        print(f"[SS14Auth] user={uuid} error={error}")
        return "Сервис авторизации недоступен"


@has_any_role(*ROLE_ACCESS_MODERATORS)
@bot.command(name="check_nick")
async def check_nick_command(ctx, nickname: str, server: str = DEFAULT_DB_SERVER):
    server_name, error = resolve_server_for_command(server, db_required=True)
    if error:
        await ctx.send(error)
        return

    data, related_accounts = await ss14_db.get_all_player_info(nickname, server_name)

    if not data:
        await ctx.send("Игрок не найден.")
        return

    player_id, guid, first_seen_time, last_seen_user_name, last_seen_time, last_seen_address, last_seen_hwid = data

    first_seen_formatted = first_seen_time.strftime("%Y-%m-%d %H:%M:%S") if isinstance(first_seen_time, datetime) else "Неизвестно"
    last_seen_time_formatted = last_seen_time.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_seen_time, datetime) else "Неизвестно"

    hwid_message = last_seen_hwid.hex() if last_seen_hwid else "Нет"
    creation_date = await get_creation_date(guid)

    discord_id = await ss14_db.get_discord_info_by_guid(guid, server_name)
    if discord_id:
        try:
            discord_member = await ctx.guild.fetch_member(int(discord_id))
            discord_name = discord_member.name
        except Exception:
            discord_name = "Неизвестно"
        discord_message = f"<@{discord_id}> · {discord_name} · `{discord_id}`"
    else:
        discord_message = "Discord не привязан."

    filtered_related_accounts = [
        acc for acc in related_accounts 
        if acc[0].casefold() not in CHECK_NICK_ACCOUNT_WHITELIST 
        and acc[0].casefold() != last_seen_user_name.casefold()
    ]

    related_lines = []
    for acc in filtered_related_accounts:
        related_user_name, related_address, related_hwid, related_last_seen_time = acc

        related_last_seen_time_str = (
            related_last_seen_time.strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(related_last_seen_time, datetime)
            else "Неизвестно"
        )

        matches = []
        if related_address == last_seen_address:
            matches.append("IP")
        if related_hwid == last_seen_hwid:
            matches.append("HWID")
        if matches:
            related_lines.append(f"`{related_user_name}` · {', '.join(matches)} · {related_last_seen_time_str}")

    embed = disnake.Embed(
        title=f"Игрок · {last_seen_user_name}"[:256],
        description=f"Сервер `{server_name.upper()}` · внутренний ID `{player_id}`",
        color=COLOR_DANGER,
    )
    embed.add_field(
        name="Активность",
        value=f"Первый вход: {first_seen_formatted}\nПоследний вход: {last_seen_time_formatted}\nСоздан: {creation_date}",
        inline=False,
    )
    embed.add_field(name="Идентификаторы", value=f"GUID: `{guid}`\nHWID: `{hwid_message}`", inline=False)
    embed.add_field(name="Discord", value=discord_message, inline=False)

    related_text = "\n".join(related_lines) or "Совпадений не найдено"
    while related_text and len(embed.fields) < 25:
        chunk = related_text[:1024]
        if len(related_text) > 1024 and "\n" in chunk:
            chunk = chunk.rsplit("\n", 1)[0]
        embed.add_field(
            name="Связанные аккаунты" if len(embed.fields) == 3 else "Связанные аккаунты · продолжение",
            value=chunk,
            inline=False,
        )
        related_text = related_text[len(chunk):].lstrip()
    await ctx.send(embed=embed)
