import uuid

from disnake.ext.commands import has_any_role

from bot_init import bot, ss14_db
from dataConfig import ROLE_ACCESS_TOP_HEADS
from tasks.discord_auth import set_linked_role_for_discord_id


@has_any_role(*ROLE_ACCESS_TOP_HEADS)
@bot.command(name="link_account")
async def link_command(ctx, guid: str, ds_id: str):
    if await ss14_db.is_linked(ds_id):
        await ctx.send("Уже привязан.")
        return

    try:
        uuid.UUID(guid)
    except ValueError:
        await ctx.send(f"Невалидный UID {guid} (символов: {len(guid)})")
        return

    success, message = await ss14_db.link_user(guid, ds_id)
    if success:
        await set_linked_role_for_discord_id(ds_id, True)
        await ctx.send(message)
        return

    await ctx.send(f"Ошибка: {message}")
