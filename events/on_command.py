from datetime import datetime

from bot_init import bot
from template_embed import embed_log
from disnake import Embed
from dataConfig import LOG_CHANNEL_ID

@bot.event
async def on_command(ctx):
    embed = Embed(title=embed_log["title"], color=embed_log["color"])
    value_map = {
        "ctx.command": ctx.command,
        "ctx.author": ctx.author,
        "ctx.author.id": ctx.author.id,
        "ctx.message.jump_url": ctx.message.jump_url,
        "datetime.now().strftime('%Y-%m-%d %H:%M:%S')": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    for field in embed_log["fields"]:
        raw_value = field["value"]
        value = value_map.get(raw_value, raw_value)
        embed.add_field(name=field["name"], value=value, inline=field["inline"])

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel is None:
        try:
            log_channel = await bot.fetch_channel(LOG_CHANNEL_ID)
        except Exception:
            return

    await log_channel.send(embed=embed)
