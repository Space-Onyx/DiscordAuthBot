import disnake
from bot_init import bot
from dataConfig import VACATION_ROLE_ID, GENERAL_ACCESS
from disnake.ext.commands import has_any_role


def _find_role(ctx, value: str):
    if value.startswith("<@&") and value.endswith(">") and value[3:-1].isdigit():
        return ctx.guild.get_role(int(value[3:-1]))
    return disnake.utils.get(ctx.guild.roles, name=value.strip())


def _role_member_lines(role, mentions: bool) -> list[str]:
    lines = []
    for member in role.members:
        if member.bot:
            continue
        suffix = " (в отпуске)" if VACATION_ROLE_ID and member.get_role(VACATION_ROLE_ID) else ""
        lines.append(f"{member.mention if mentions else member.display_name}{suffix}")
    return lines


async def _send_role_members(ctx, value: str, mentions: bool) -> None:
    role = _find_role(ctx, value)
    if not role:
        await ctx.send("Роль не найдена.")
        return

    lines = _role_member_lines(role, mentions)
    if not lines:
        await ctx.send("Нет пользователей с этой ролью.")
        return

    chunks: list[str] = []
    current = ""
    for line in lines:
        candidate = f"{current}\n{line}" if current else line
        if len(candidate) > 1900:
            chunks.append(current)
            current = line
        else:
            current = candidate
    if current:
        chunks.append(current)

    for index, chunk in enumerate(chunks):
        title = f"{role.name} ({len(lines)})" if index == 0 else None
        await ctx.send(embed=disnake.Embed(title=title, description=chunk, color=role.color))


@bot.command(name='user_role')
async def user_role_command(ctx, *, role: str):
    await _send_role_members(ctx, role, mentions=False)

@has_any_role(*GENERAL_ACCESS)
@bot.command(name='user_role_mention')
async def user_role_mention_command(ctx, *, role: str):
    await _send_role_members(ctx, role, mentions=True)
