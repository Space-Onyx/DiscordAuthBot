from datetime import datetime, timedelta
from disnake import Embed
from template_embed import embed_status


def compute_status_text(run_level: int | None) -> str:
    if run_level == 1:
        return "Раунд идет"
    if run_level == 0:
        return "Ожидание"
    return "Неизвестно"


def compute_round_length_text(round_start_time: str | None) -> str:
    if not round_start_time:
        return "Не начался"
    try:
        start_dt = datetime.fromisoformat(round_start_time.replace("Z", "+00:00"))
        start_dt = start_dt + timedelta(hours=3)
        now_dt = datetime.utcnow() + timedelta(hours=3)
        elapsed = now_dt - start_dt
        if elapsed.total_seconds() < 0:
            elapsed = timedelta(0)
        total_minutes = int(elapsed.total_seconds() // 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours:02d}ч {minutes:02d}м"
    except Exception:
        return "Не начался"


def build_status_embed(data: dict, server_label: str, status_text: str, round_length_text: str) -> Embed:
    title = data.get("name", "Без названия")
    values = {
        "online": f"{data.get('players', 0)}/{data.get('soft_max_players', 0)}",
        "map": data.get("map", "Неизвестно"),
        "preset": data.get("preset", "Неизвестно"),
        "status": status_text,
        "duration": round_length_text,
        "round_id": data.get("round_id", "—"),
        "bunker": "Включен" if data.get("panic_bunker") else "Выключен",
    }

    embed = Embed(title=title, color=embed_status["color"])
    for field in embed_status["fields"]:
        key = field.get("key")
        value = values.get(key, "—")
        embed.add_field(name=field["name"], value=value, inline=field.get("inline", False))

    embed.set_footer(text=f"Сервер: {server_label}")
    return embed
