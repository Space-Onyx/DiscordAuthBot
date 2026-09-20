import aiohttp
from disnake import Embed
from disnake.ext.commands import has_any_role

from bot_init import bot
from dataConfig import DEFAULT_SERVER_NAME, ROLE_ACCESS_MODERATORS, ROLE_ACCESS_EVENTOLOGY, build_admin_headers, build_admin_url
from server_utils import resolve_server_for_command
from template_embed import COLOR_PRIMARY


def add_chunked_fields(embed, name, value, max_length=1024, inline=False):
    """Разбивает длинное значение на несколько полей."""
    chunks = []
    remaining = value
    while remaining:
        if len(remaining) <= max_length:
            chunks.append(remaining)
            break
        split_at = remaining.rfind("\n", 0, max_length + 1)
        if split_at <= 0:
            split_at = max_length
        chunks.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].lstrip()

    for i, value_chunk in enumerate(chunks):
        if len(embed.fields) >= 25:
            return
        field_name = name if i == 0 else f"{name} (часть {i + 1})"
        embed.add_field(name=field_name, value=value_chunk, inline=inline)


@has_any_role(*ROLE_ACCESS_MODERATORS, *ROLE_ACCESS_EVENTOLOGY)
@bot.command(name="admin_info")
async def admin_info_command(ctx, server: str = DEFAULT_SERVER_NAME):
    server_name, error = resolve_server_for_command(server)
    if error:
        await ctx.send(error)
        return

    url = build_admin_url("/admin/info", server_name)
    if not url:
        await ctx.send("Не удалось сформировать URL admin API.")
        return

    headers = build_admin_headers(server_name)
    if headers is None:
        await ctx.send(
            f"Не настроен ADMIN API токен для сервера {server_name.upper()}. "
            f"Укажите SERVER_*_ADMIN_API_TOKEN или глобальный ADMIN_API."
        )
        return

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    await ctx.send(f"Ошибка: код {resp.status}")
                    return

                data = await resp.json()
                players = data.get("Players", [])
                values = {
                    "ID раунда": str(data.get("RoundId", "Не задано")),
                    "Карта": str((data.get("Map") or {}).get("Name", "Не задано")),
                    "MOTD": str(data.get("MOTD", "Нет сообщения")),
                    "Режим": str(data.get("GamePreset", "Не задано")),
                    "Игроки": "\n".join(
                        f"{p.get('Name', '?')} - {'Админ' if p.get('IsAdmin') else 'Игрок'} ({p.get('PingUser', '?')} ms)"
                        for p in players if not p.get("IsDeadminned")
                    ) or "Нет игроков",
                    "Деадмины": "\n".join(
                        f"{p.get('Name', '?')} ({p.get('PingUser', '?')} ms)"
                        for p in players if p.get("IsDeadminned")
                    ) or "Нет",
                    "Активные админы": "\n".join(
                        str(p.get("Name", "?"))
                        for p in players if p.get("IsAdmin") and not p.get("IsDeadminned")
                    ) or "Нет",
                    "Правила игры": "\n".join(map(str, data.get("GameRules", []))) or "Нет правил",
                    "Паник-бункер": "\n".join(
                        f"{key}: {value}" for key, value in data.get("PanicBunker", {}).items() if value is not None
                    ) or "Не активирован",
                }
                embed = Embed(title=f"Сервер · {server_name.upper()}"[:256], color=COLOR_PRIMARY)
                for name, value in values.items():
                    add_chunked_fields(embed, name, value)

                await ctx.send(embed=embed)
    except Exception as error:
        print(f"[AdminInfo] server={server_name} error={error}")
        await ctx.send("Admin API недоступен. Попробуйте позже.")
