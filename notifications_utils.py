from disnake import Embed
from template_embed import embed_ahelp, embed_ban, embed_round


def format_duration_text(total_seconds: int | float | None) -> str:
    if total_seconds is None:
        return "—"
    try:
        total_minutes = int(total_seconds // 60)
    except TypeError:
        return "—"
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours:02d}ч {minutes:02d}м"


def build_round_embed(event: dict, server_label: str) -> Embed:
    kind = event.get("type") or "started"
    cfg = embed_round.get(kind, embed_round["started"])

    values = {
        "round_id": str(event.get("roundId", "—")),
        "map": event.get("mapName") or "Неизвестно",
        "preset": event.get("preset") or "Неизвестно",
        "online": str(event.get("playerCount", "—")),
        "duration": format_duration_text(event.get("durationSeconds")),
    }

    embed = Embed(title=cfg.get("title", "Раунд"), color=cfg.get("color", 0x00FF00))
    for field in cfg.get("fields", []):
        key = field.get("key")
        embed.add_field(
            name=str(field["name"])[:256],
            value=str(values.get(key, "—"))[:1024],
            inline=field.get("inline", False),
        )

    embed.set_footer(text=f"Сервер: {server_label}"[:2048])
    return embed


def build_ahelp_embed(conversation: dict, server_label: str, round_id: int | str | None, run_level: str | None) -> Embed:
    ckey = conversation.get("ckey") or "?"
    character_name = conversation.get("characterName")
    title = f"{embed_ahelp.get('title', 'Ахелп')}: {ckey}"
    if character_name:
        title += f" ({character_name})"
    title = title[:256]

    embed = Embed(
        title=title,
        color=embed_ahelp.get("color", 0x0099FF),
        description=str(conversation.get("transcript") or "—")[:4096],
    )
    embed.set_footer(text=f"Сервер: {server_label} | Раунд: {round_id} | {run_level or '—'}"[:2048])
    return embed


def build_role_ping_content(role_id: int | None) -> str | None:
    if not role_id:
        return None
    return f"<@&{role_id}>"


def build_ban_embed(event: dict, server_label: str | None = None) -> Embed:
    embed = Embed(
        title=str(event.get("title") or "Бан")[:256],
        color=event.get("color", embed_ban.get("color", 0x8B0000)),
        description=str(event.get("description") or "—")[:4096],
    )
    footer = event.get("footer")
    if footer:
        embed.set_footer(text=str(footer)[:2048])
    elif server_label:
        embed.set_footer(text=str(server_label)[:2048])
    return embed
