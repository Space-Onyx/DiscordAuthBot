import aiohttp
from disnake.ext.commands import has_any_role

from bot_init import bot, ss14_db
from dataConfig import ROLE_ACCESS_MODERATORS, build_admin_headers, build_admin_url
from server_utils import parse_server_from_tokens


@has_any_role(*ROLE_ACCESS_MODERATORS)
@bot.command(name="ban")
async def ban_command(ctx, nickname: str, *args: str):
    parsed_args, server_name, error = parse_server_from_tokens(
        args,
        db_required=False,
        trailing_server_min_tokens=3,
    )
    if error:
        await ctx.send(error)
        return

    if len(parsed_args) < 2:
        await ctx.send(
            "Использование: &ban <nickname> <reason...> <time_minutes> [server]\n"
            "Также поддерживается: --server <name> | -s <name> | server=<name>"
        )
        return

    reason = " ".join(parsed_args[:-1]).strip()
    time = parsed_args[-1].strip()

    if not reason:
        await ctx.send("Укажите причину бана.")
        return

    if not time.isdigit():
        await ctx.send("Срок бана указывается в минутах.")
        return

    discord_id = str(ctx.author.id)

    admin_guid = await ss14_db.get_player_guid_by_discord_id(discord_id, server_name)
    if not admin_guid:
        await ctx.send("Привяжите аккаунт Discord.")
        return

    admin_name = await ss14_db.get_admin_name(admin_guid, server_name)
    if not admin_name:
        await ctx.send("Ваш аккаунт SS14 не найден на этом сервере.")
        return

    player_guid = await ss14_db.get_player_guid(nickname, server_name)
    if not player_guid:
        await ctx.send("Игрок не найден на этом сервере.")
        return

    url = build_admin_url("/admin/actions/server_ban", server_name)
    if not url:
        await ctx.send("Admin API не настроен.")
        return

    post_data = {"NickName": nickname, "Reason": reason, "Time": time}
    actor_data = {"Guid": str(admin_guid), "Name": admin_name}

    headers = build_admin_headers(server_name, actor_data)
    if headers is None:
        await ctx.send(
            f"Не настроен ADMIN API токен для сервера {server_name.upper()}. "
            f"Укажите SERVER_*_ADMIN_API_TOKEN или глобальный ADMIN_API."
        )
        return

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.post(url, headers=headers, json=post_data) as resp:
                if resp.status == 200:
                    await ctx.send(
                        f"✅ {nickname} забанен на {time} мин. · {server_name.upper()}\nПричина: {reason}"
                    )
                else:
                    await ctx.send(f"Admin API вернул код {resp.status}.")
    except Exception as error:
        print(f"[Ban] server={server_name} target={nickname} error={error}")
        await ctx.send("Admin API недоступен.")
