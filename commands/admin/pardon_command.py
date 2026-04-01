from bot_init import bot
from disnake.ext.commands import has_any_role
from bot_init import ss14_db
from dataConfig import ROLE_ACCESS_DEPARTAMENT_OF_UNBAN_ADMIN
from datetime import datetime

import pytz

'''Команда для разбана игрока с сервера ASTRA'''
@has_any_role(*ROLE_ACCESS_DEPARTAMENT_OF_UNBAN_ADMIN)
@bot.command(name="pardon")
async def pardon_command(ctx, ban_id: int):
    ds_id = str(ctx.author.id)

    admin_guid = await ss14_db.get_player_guid_by_discord_id(ds_id)
    if not admin_guid:
        await ctx.send(f"Ваш GUID не найден в БД. Привяжите свой аккакнут в канале #🔗▏привязка-аккаунта - https://discord.com/channels/901772674865455115/1351213738774237184.")
        return

    time_ban = datetime.now(pytz.timezone("Europe/Moscow"))

    reply, message = await ss14_db.unban_player(ban_id, admin_guid, time_ban)

    if not reply:
        await ctx.send(f"{message}")
        return
    
    await ctx.send(f"{message}")
