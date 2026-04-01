from bot_init import bot, ss14_db
from dataConfig import ROLE_ACCESS_OBSERVER_ADMIN
from disnake.ext.commands import has_any_role


@has_any_role(*ROLE_ACCESS_OBSERVER_ADMIN)
@bot.command(name="logs")
async def logs_command(ctx, username: str, round_id: int, db_name: str = "astra"):
    try:
        db_name = db_name.lower()
        if db_name not in ("astra", "dev"):
            await ctx.send("Неверный сервер: astra или dev")
            return

        guid_admin = await ss14_db.get_player_guid(username, db_name)
        if not guid_admin:
            await ctx.send("Пользователь не найден в БД.")
            return

        results = await ss14_db.get_logs_by_round(username, round_id, db_name)
        if not results:
            await ctx.send("Не найдено подозрительных логов админ-абуза.")
            return

        output = "\n\n".join(f"{row['message']}" for row in results)
        chunks = [output[i:i + 2000] for i in range(0, len(output), 2000)]
        for chunk in chunks:
            await ctx.send(chunk)
    except Exception as e:
        await ctx.send(f"⚠️ Ошибка при получении логов: {e}")
