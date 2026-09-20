from bot_init import bot
from disnake import Embed
from template_embed import embed_help


@bot.command(name="help")
async def help_command(ctx):
    embed = Embed(title=embed_help["title"], color=embed_help["color"])
    for field in embed_help["fields"]:
        embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])

    if bot.user is not None:
        embed.set_author(name=bot.user.display_name, icon_url=bot.user.display_avatar.url)

    await ctx.send(embed=embed)
