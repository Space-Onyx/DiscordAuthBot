from bot_init import bot, ss14_db
from disnake.ext.commands import has_any_role
from dataConfig import ROLE_ACCESS_MODERATORS, ROLE_ACCESS_EVENTOLOGY

@has_any_role(*ROLE_ACCESS_MODERATORS, *ROLE_ACCESS_EVENTOLOGY)
@bot.command(name="get_ckey")
async def get_ckey_command(ctx, discord_id: str):
    discord_id = discord_id.strip().removeprefix("<@").removeprefix("!").removesuffix(">")
    if not discord_id.isdigit() or len(discord_id) > 20:
        await ctx.send("Некорректный Discord ID.")
        return
    player_guid = await ss14_db.get_player_guid_by_discord_id(discord_id)
    if not player_guid:
        await ctx.send("Привязанный игрок не найден.")
        return

    player_name = await ss14_db.get_player_name(player_guid)

    await ctx.send(f"Discord ID `{discord_id}` привязан к игроку `{player_name}`.")
