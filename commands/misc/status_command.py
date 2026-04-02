import aiohttp
from datetime import datetime, timedelta
from disnake import Embed

from bot_init import bot
from dataConfig import DEFAULT_SERVER_NAME, build_status_url
from server_utils import resolve_server_for_command
from template_embed import embed_status


@bot.command(name="status")
async def status_command(ctx, server: str = DEFAULT_SERVER_NAME):
    server_name, error = resolve_server_for_command(server)
    if error:
        await ctx.send(error)
        return

    url = build_status_url(server_name)
    if not url:
        await ctx.send("Не удалось сформировать URL статуса для выбранного сервера.")
        return

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send(f"Ошибка: код {resp.status}")
                    return

                data = await resp.json()
                run_level = data.get("run_level")
                if run_level == 1:
                    status_text = "Раунд идет"
                elif run_level == 0:
                    status_text = "Ожидание"
                else:
                    status_text = "Неизвестно"

                round_start_time = data.get("round_start_time")
                round_length_text = "Не начался"
                if round_start_time:
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
                        round_length_text = f"{hours:02d}ч {minutes:02d}м"
                    except Exception:
                        round_length_text = "Не начался"

                title_value = embed_status["title"]
                try:
                    title_value = eval(title_value)
                except Exception:
                    title_value = str(title_value)

                embed = Embed(title=title_value, color=embed_status["color"])
                if "description" in embed_status:
                    embed.description = eval(embed_status["description"])
                for field in embed_status["fields"]:
                    embed.add_field(name=field["name"], value=eval(field["value"]), inline=field["inline"])
                embed.set_footer(text=f"Сервер: {server_name}")
                await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Ошибка: {e}")
