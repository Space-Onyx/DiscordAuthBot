import aiohttp
from disnake.ext import commands

from bot_init import bot
from dataConfig import DEFAULT_SERVER_NAME, build_status_url
from server_utils import resolve_server_for_command
from status_utils import build_status_embed, compute_round_length_text, compute_status_text


@bot.command(name="status")
@commands.cooldown(3, 20, commands.BucketType.user)
async def status_command(ctx, server: str = DEFAULT_SERVER_NAME):
    server_name, error = resolve_server_for_command(server)
    if error:
        await ctx.send(error)
        return

    url = build_status_url(server_name)
    if not url:
        await ctx.send("URL статуса не настроен.")
        return

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send(f"Сервер вернул код {resp.status}.")
                    return

                data = await resp.json()
                status_text = compute_status_text(data.get("run_level"))
                round_length_text = compute_round_length_text(data.get("round_start_time"))
                embed = build_status_embed(data, status_text, round_length_text)
                await ctx.send(embed=embed)
    except Exception as error:
        print(f"[Status] server={server_name} error={error}")
        await ctx.send("Статус недоступен.")
