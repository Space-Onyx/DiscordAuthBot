import disnake
from disnake.ext.commands import has_any_role

from bot_init import bot, ss14_db
from dataConfig import DEFAULT_DB_SERVER, ROLE_ACCESS_MODERATORS, ROLE_ACCESS_EVENTOLOGY
from server_utils import resolve_server_for_command
from template_embed import COLOR_DANGER


@has_any_role(*ROLE_ACCESS_MODERATORS, *ROLE_ACCESS_EVENTOLOGY)
@bot.command(name="notelist")
async def player_notes_command(ctx, nickname: str, server: str = DEFAULT_DB_SERVER):
    server_name, error = resolve_server_for_command(server, db_required=True)
    if error:
        await ctx.send(error)
        return

    notes = await ss14_db.search_notes_player(nickname, server_name)

    if not notes:
        embed = disnake.Embed(
            title="Заметки не найдены",
            description=f"У `{nickname}` нет заметок на `{server_name.upper()}`.",
            color=COLOR_DANGER,
        )
        await ctx.send(embed=embed)
        return

    embeds = []
    for index, note in enumerate(notes):
        if index % 10 == 0:
            embed = disnake.Embed(
                title=f"Заметки · {nickname} · {server_name.upper()}"[:256],
                description=f"Записей: **{len(notes)}**",
                color=COLOR_DANGER,
            )
            embeds.append(embed)
        note_id, created_at, message, severity, secret, last_edited_at, last_edited_by_id, player_id, last_seen_user_name, created_by_name = note
        created_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else "?"
        note_message = message.replace("\n", " ") if message else "Нет сообщения"

        info = (
            f"{note_message}\n"
            f"`{created_str}` · {created_by_name or 'неизвестно'}"
        )

        if last_edited_at:
            edited_str = last_edited_at.strftime("%Y-%m-%d %H:%M:%S")
            info += f"\nИзменено: `{edited_str}`"

        embed.add_field(name=f"#{note_id}", value=info[:1024], inline=False)

    for embed in embeds:
        await ctx.send(embed=embed)
