from datetime import datetime, timedelta, timezone
from disnake import Embed
from template_embed import COLOR_DANGER, COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, embed_status


def compute_status_text(run_level: int | str | None) -> str:
    try:
        level = int(run_level) if run_level is not None else None
    except (TypeError, ValueError):
        level = None

    return {
        0: "Лобби",
        1: "Раунд идёт",
        2: "Раунд завершён",
    }.get(level, "Неизвестно")


def compute_round_length_text(round_start_time: str | None) -> str:
    if not round_start_time:
        return "Не начался"
    try:
        start_dt = datetime.fromisoformat(round_start_time.replace("Z", "+00:00"))
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc)
        start_dt = start_dt + timedelta(hours=3)
        now_dt = datetime.now(timezone.utc) + timedelta(hours=3)
        elapsed = now_dt - start_dt
        if elapsed.total_seconds() < 0:
            elapsed = timedelta(0)
        total_minutes = int(elapsed.total_seconds() // 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours:02d}ч {minutes:02d}м"
    except Exception:
        return "Не начался"


def build_status_embed(data: dict, status_text: str, round_length_text: str) -> Embed:
    title = str(data.get("name") or "Без названия")[:256]
    values = {
        "online": f"{data.get('players', 0)}/{data.get('soft_max_players', 0)}",
        "map": data.get("map", "Неизвестно"),
        "preset": data.get("preset", "Неизвестно"),
        "status": status_text,
        "duration": round_length_text,
        "round_id": data.get("round_id", "—"),
        "bunker": "Включён" if data.get("panic_bunker") else "Выключен",
    }

    color = {
        "Раунд идёт": COLOR_SUCCESS,
        "Лобби": COLOR_WARNING,
        "Раунд завершён": COLOR_DANGER,
        "Неизвестно": COLOR_DANGER,
    }.get(status_text, COLOR_PRIMARY)
    embed = Embed(title=title, color=color, timestamp=datetime.now(timezone.utc))
    for field in embed_status["fields"]:
        key = field.get("key")
        value = str(values.get(key, "—"))[:1024]
        embed.add_field(name=field["name"], value=value, inline=field.get("inline", False))

    embed.set_footer(text="Обновлено")
    return embed
