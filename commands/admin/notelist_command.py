import disnake
from disnake.ext.commands import has_any_role

from bot_init import bot, ss14_db
from dataConfig import DEFAULT_DB_SERVER, ROLE_ACCESS_ADMIN
from server_utils import resolve_server_for_command


@has_any_role(*ROLE_ACCESS_ADMIN)
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
            description=f"{nickname} без заметок на {server_name.upper()}.",
            color=0xFF0000,
        )
        await ctx.send(embed=embed)
        return

    embed = disnake.Embed(title=f"Заметки {nickname} ({len(notes)})", color=0x8B0000)
    embed.description = f"Сервер: {server_name.upper()}"

    for note in notes:
        note_id, created_at, message, severity, secret, last_edited_at, last_edited_by_id, player_id, last_seen_user_name, created_by_name = note
        created_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else "?"
        note_message = message.replace("\n", " ") if message else "Нет сообщения"

        info = (
            f"**Дата:** {created_str}\n"
            f"**Админ:** {created_by_name or '?'}\n"
            f"**Сообщение:** {note_message}"
        )

        if last_edited_at:
            edited_str = last_edited_at.strftime("%Y-%m-%d %H:%M:%S")
            info += f"\n**Редактировано:** {edited_str}"

        embed.add_field(name=f"---------------\nЗаметка #{note_id}", value=info, inline=False)

    await ctx.send(embed=embed)
