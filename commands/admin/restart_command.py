import aiohttp

from bot_init import bot
from dataConfig import ADDRESS_ASTRA, ADDRESS_DEV, DATA_ASTRA, DATA_DEV, HEADERS_ASTRA, HEADERS_DEV, ROLE_ACCESS_HEADS
from disnake.ext.commands import has_any_role

'''Команда для рестарта сервера ASTRA/DEV'''
@has_any_role(*ROLE_ACCESS_HEADS)
@bot.command(name="restart")
async def restart_command(ctx, server: str = "astra"):
    if server.lower() == "astra":
        address = ADDRESS_ASTRA
        instance = "ASTRA"
        port = 5000
        data = DATA_ASTRA
        headers = HEADERS_ASTRA
    elif server.lower() == "dev":
        address = ADDRESS_DEV
        instance = "DEV"
        port = 5001
        data = DATA_DEV
        headers = HEADERS_DEV
    else:
        await ctx.send("Неверный сервер: dev или astra")
        return

    url = f"http://{address}:{port}/instances/{instance}/restart"

    await ctx.send(f"Запущен рестарт {server.upper()} сервера...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers) as resp:
                if resp.status == 200:
                    await ctx.send(f"✅ Рестарт {server.upper()} выполнен.")
                else:
                    await ctx.send(f"Ошибка: код {resp.status}")
    except Exception as e:
        await ctx.send(f"Ошибка: {e}")
