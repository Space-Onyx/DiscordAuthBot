from disnake.ext.commands import has_any_role

from bot_init import bot, ss14_db
from dataConfig import ROLE_ACCESS_TOP_HEADS
from tasks.discord_auth import set_linked_role_for_discord_id


@has_any_role(*ROLE_ACCESS_TOP_HEADS)
@bot.command(name="link_account")
async def link_command(ctx, link_code: str, ds_id: str = None):
    discord_id = str(ctx.author.id) if ds_id is None else str(ds_id).strip()

    success, message = await ss14_db.link_user_by_code(link_code, discord_id)
    if success:
        await set_linked_role_for_discord_id(discord_id, True)

    await ctx.send(message)
