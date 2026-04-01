from bot_init import bot
from disnake import Embed
from template_embed import embed_help


@bot.command(name="help")
async def help_command(ctx):
    embed = Embed(title=embed_help["title"], color=embed_help["color"])
    for field in embed_help["fields"]:
        embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])

    # display_avatar всегда доступен (и для дефолтной аватарки тоже).
    if bot.user is not None:
        embed.set_thumbnail(url=bot.user.display_avatar.url)

    await ctx.send(embed=embed)
