from disnake.ext.commands import has_any_role

from bot_init import bot, ss14_db
from dataConfig import ROLE_ACCESS_TOP_HEADS
from tasks.discord_auth import set_linked_role_for_discord_id


"""Команда для отвязки аккаунта."""
@has_any_role(*ROLE_ACCESS_TOP_HEADS)
@bot.command(name="unlink_account")
async def unlink_account_command(ctx, discord_id: str = None):
    if discord_id is None:
        discord_id = str(ctx.author.id)
    discord_id = str(discord_id).strip()
    if not discord_id.isdigit() or len(discord_id) > 20:
        await ctx.send("Некорректный Discord ID.")
        return

    try:
        if not await ss14_db.is_linked(discord_id):
            await ctx.send("Аккаунт не привязан.")
            return

        success, message = await ss14_db.unlink_user(discord_id)
    except Exception as error:
        print(f"[DiscordAuth] manual unlink user={discord_id} error={error}")
        await ctx.send("Отвязка недоступна.")
        return
    if success:
        await set_linked_role_for_discord_id(discord_id, False)

    await ctx.send(message)
