from datetime import datetime

import aiohttp
import disnake
from disnake.ext.commands import has_any_role

from bot_init import bot, ss14_db
from dataConfig import DEFAULT_DB_SERVER, ROLE_ACCESS_ADMIN
from server_utils import resolve_server_for_command


async def get_creation_date(uuid: str):
    url = f"https://auth.spacestation14.com/api/query/userid?userid={uuid}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    player_date = data.get("createdTime", None)
                    if player_date:
                        date_obj = datetime.fromisoformat(player_date)
                        unix = int(date_obj.timestamp())
                        return f"<t:{unix}:f>"
                    return "Дата не найдена"
                return f"Ошибка: код {resp.status}"
    except Exception as e:
        return f"Ошибка: {e}"


@has_any_role(*ROLE_ACCESS_ADMIN)
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
        discord_message = f"Привязан Discord: <@{discord_id}> ({discord_name}, ID: {discord_id})"
    else:
        discord_message = "Discord не привязан."

    related_accounts_str = "Совпадение по аккаунтам:\n"
    if related_accounts:
        for acc in related_accounts:
            related_user_name, related_address, related_hwid, related_last_seen_time = acc
            if related_user_name == last_seen_user_name:
                continue

            related_last_seen_time_str = (
                related_last_seen_time.strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(related_last_seen_time, datetime)
                else "Неизвестно"
            )

            if related_address == last_seen_address and related_hwid != last_seen_hwid:
                related_accounts_str += f"{related_user_name} [IP] | Последний заход: {related_last_seen_time_str}\n"
            elif related_hwid == last_seen_hwid and related_address != last_seen_address:
                related_accounts_str += f"{related_user_name} [HWID] | Последний заход: {related_last_seen_time_str}\n"
            elif related_hwid == last_seen_hwid and related_address == last_seen_address:
                related_accounts_str += f"{related_user_name} [IP, HWID] | Последний заход: {related_last_seen_time_str}\n"

        if related_accounts_str == "Совпадение по аккаунтам:\n":
            related_accounts_str += "Не найдены"
    else:
        related_accounts_str += "Не найдены"

    description = (
        f"Сервер БД: {server_name.upper()}\n\n"
        f"Первый заход: {first_seen_formatted}\n"
        f"Последний заход: {last_seen_time_formatted}\n"
        f"Дата создания: {creation_date}\n\n"
        f"HWID: {hwid_message}\n"
        f"GUID: {guid}\n\n"
        f"{discord_message}\n\n"
        f"{related_accounts_str}"
    )

    embed = disnake.Embed(title=f"{last_seen_user_name} | ID {player_id}", description=description, color=0xFF0000)
    await ctx.send(embed=embed)
