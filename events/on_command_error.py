import traceback

from bot_init import bot
from disnake.ext import commands


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Неизвестная команда.")
        return

    if isinstance(error, (commands.MissingAnyRole, commands.MissingPermissions)):
        await ctx.send("❌ Недостаточно прав.")
        return

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Укажите `{error.param.name}`.")
        return

    if isinstance(error, commands.BadArgument):
        await ctx.send("❌ Неверные аргументы.")
        return

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Повторите через {error.retry_after:.1f} сек.")
        return

    if isinstance(error, commands.CommandInvokeError):
        original = error.original
        print(f"[CommandInvokeError] command={ctx.command} user={ctx.author} error={original}")
        traceback.print_exception(type(original), original, original.__traceback__)
        await ctx.send("⚠️ Команда завершилась с ошибкой.")
        return

    print(f"[UnhandledCommandError] command={ctx.command} user={ctx.author} error={error}")
    traceback.print_exception(type(error), error, error.__traceback__)
    await ctx.send("⚠️ Команда завершилась с ошибкой.")
