from disnake.ext.commands import has_any_role
import disnake

from bot_init import bot, ss14_db
from dataConfig import ROLE_ACCESS_TOP_HEADS
from tasks.discord_auth import set_linked_role_for_discord_id


@has_any_role(*ROLE_ACCESS_TOP_HEADS)
@bot.command(name="link_account")
async def link_command(ctx, ckey: str, link_code: str, ds_id: str = None):
    try:
        await ctx.message.delete()
    except disnake.HTTPException:
        await ctx.send("Не удалось удалить код. Используйте кнопку привязки.")
        return

    discord_id = str(ctx.author.id) if ds_id is None else str(ds_id).strip()
    if not discord_id.isdigit() or len(discord_id) > 20:
        await ctx.send("Некорректный Discord ID.")
        return

    try:
        success, message = await ss14_db.link_user_by_code(ckey, link_code, discord_id)
    except Exception as error:
        print(f"[DiscordAuth] manual link user={discord_id} error={error}")
        await ctx.send("Привязка недоступна.")
        return
    if success:
        await set_linked_role_for_discord_id(discord_id, True)

    await ctx.send(message)
