import asyncio
import uuid

import disnake
from disnake.ext import tasks

from bot_init import bot, ss14_db
from dataConfig import CHANNEL_AUTH_DISCORD, CHANNEL_LOG_AUTH_DISCORD, LINKED_ACCOUNT_ROLE_ID


def _resolve_linked_role_id() -> int | None:
    if LINKED_ACCOUNT_ROLE_ID in (None, "", 0, "0"):
        return None
    try:
        return int(LINKED_ACCOUNT_ROLE_ID)
    except (TypeError, ValueError):
        print(f"[LinkedRoleSync] Invalid LINKED_ACCOUNT_ROLE_ID: {LINKED_ACCOUNT_ROLE_ID}")
        return None


async def _safe_send_tech_log(message: str):
    channel = bot.get_channel(CHANNEL_LOG_AUTH_DISCORD)
    if channel is None:
        try:
            channel = await bot.fetch_channel(CHANNEL_LOG_AUTH_DISCORD)
        except disnake.HTTPException:
            return
    try:
        await channel.send(message)
    except disnake.HTTPException:
        return


async def _get_member(guild: disnake.Guild, member_id: int):
    member = guild.get_member(member_id)
    if member is not None:
        return member
    try:
        return await guild.fetch_member(member_id)
    except (disnake.NotFound, disnake.Forbidden, disnake.HTTPException):
        return None


async def _set_linked_role_in_guild(guild: disnake.Guild, member_id: int, linked: bool) -> tuple[int, int]:
    role_id = _resolve_linked_role_id()
    if role_id is None:
        return 0, 0

    role = guild.get_role(role_id)
    if role is None:
        print(f"[LinkedRoleSync] Role {role_id} not found in guild {guild.id}")
        return 0, 0

    member = await _get_member(guild, member_id)
    if member is None:
        print(f"[LinkedRoleSync] Member {member_id} not found in guild {guild.id}")
        return 0, 0

    has_role = role in member.roles
    if linked and not has_role:
        try:
            await member.add_roles(role, reason="SS14 account linked")
            return 1, 0
        except disnake.Forbidden:
            print(f"[LinkedRoleSync] Forbidden add role {role_id} to member {member_id} in guild {guild.id}")
            return 0, 0
        except disnake.HTTPException as e:
            print(f"[LinkedRoleSync] HTTP add role error for {member_id}: {e}")
            return 0, 0

    if not linked and has_role:
        try:
            await member.remove_roles(role, reason="SS14 account unlinked")
            return 0, 1
        except disnake.Forbidden:
            print(f"[LinkedRoleSync] Forbidden remove role {role_id} from member {member_id} in guild {guild.id}")
            return 0, 0
        except disnake.HTTPException as e:
            print(f"[LinkedRoleSync] HTTP remove role error for {member_id}: {e}")
            return 0, 0

    return 0, 0


async def set_linked_role_for_discord_id(discord_id: str, linked: bool) -> tuple[int, int]:
    role_id = _resolve_linked_role_id()
    if role_id is None:
        return 0, 0

    try:
        member_id = int(discord_id)
    except (TypeError, ValueError):
        print(f"[LinkedRoleSync] Invalid discord_id: {discord_id}")
        return 0, 0

    added = 0
    removed = 0
    for guild in bot.guilds:
        a, r = await _set_linked_role_in_guild(guild, member_id, linked)
        added += a
        removed += r
    return added, removed


async def sync_linked_account_roles() -> tuple[int, int]:
    role_id = _resolve_linked_role_id()
    if role_id is None:
        return 0, 0

    linked_ids: set[str] = set()
    last_error = None
    for _ in range(3):
        try:
            linked_ids = await ss14_db.get_all_linked_discord_ids()
            last_error = None
            break
        except Exception as e:
            last_error = e
            await asyncio.sleep(1)

    if last_error is not None:
        print(f"[LinkedRoleSync] DB unavailable, skip cycle: {last_error}")
        return 0, 0

    added = 0
    removed = 0

    for guild in bot.guilds:
        role = guild.get_role(role_id)
        if role is None:
            continue

        for ds_id in linked_ids:
            try:
                member_id = int(ds_id)
            except (TypeError, ValueError):
                continue

            member = await _get_member(guild, member_id)
            if member is None or role in member.roles:
                continue
            try:
                await member.add_roles(role, reason="SS14 account linked")
                added += 1
            except disnake.HTTPException:
                continue

        for member in list(role.members):
            if str(member.id) in linked_ids:
                continue
            try:
                await member.remove_roles(role, reason="SS14 account unlinked")
                removed += 1
            except disnake.HTTPException:
                continue

    return added, removed


@tasks.loop(minutes=30)
async def linked_role_sync_task():
    try:
        added, removed = await sync_linked_account_roles()
        if added or removed:
            print(f"[LinkedRoleSync] Added: {added}, removed: {removed}")
    except Exception as e:
        print(f"[LinkedRoleSync] Sync error: {e}")


class NicknameModal(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Введите UID SS14",
                placeholder="UID из лобби SS14",
                custom_id="guid",
                style=disnake.TextInputStyle.short,
                required=True,
            )
        ]
        super().__init__(title="Привязка аккаунта", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.defer(ephemeral=True)
        guid = inter.text_values["guid"].strip()
        discord_id = str(inter.author.id)

        if not guid:
            await inter.send("❌ UID не может быть пустым.", ephemeral=True)
            await _safe_send_tech_log(f"⚠️ Пользователь {inter.author.name} ({discord_id}) ввёл пустой UID.")
            return

        if await ss14_db.is_linked(discord_id):
            await inter.send("❌ Аккаунт уже привязан.", ephemeral=True)
            await _safe_send_tech_log(
                f"⚠️ Пользователь {inter.author.name} ({discord_id}) пытался повторно привязать аккаунт."
            )
            return

        try:
            uuid.UUID(guid)
        except ValueError:
            await inter.send("⚠️ Вы ввели невалидный UID.", ephemeral=True)
            await _safe_send_tech_log(
                f"⚠️ Ошибка: {inter.author.name} ({discord_id}) ввёл невалидный UID {guid}."
            )
            return

        success, message = await ss14_db.link_user(guid, discord_id)
        await inter.send(message, ephemeral=True)

        if success:
            added = 0
            if inter.guild is not None:
                a, _ = await _set_linked_role_in_guild(inter.guild, inter.author.id, True)
                added += a
            else:
                a, _ = await set_linked_role_for_discord_id(discord_id, True)
                added += a

            await _safe_send_tech_log(
                f"✅ Привязка: {inter.author.name} ({discord_id}) к UID {guid}. RoleAdded={added}"
            )
            return

        await _safe_send_tech_log(
            f"⚠️ Ошибка привязки для {inter.author.name} ({discord_id}) к UID {guid}: {message}."
        )


class RegisterButton(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Привязать аккаунт", style=disnake.ButtonStyle.primary, custom_id="link_button")
    async def register(self, button, inter):
        await inter.response.send_modal(NicknameModal())


@tasks.loop(hours=12)
async def discord_auth_update():
    channel = bot.get_channel(CHANNEL_AUTH_DISCORD)
    if not channel:
        return

    embed = disnake.Embed(
        title="Привязка аккаунта SS14",
        description="Нажмите кнопку и введите UID.",
        color=0x3498DB,
    )

    pinned = []
    async for msg in channel.pins():
        pinned.append(msg)

    old_message = next((m for m in pinned if m.author == channel.guild.me), None)

    if old_message:
        await old_message.edit(embed=embed, view=RegisterButton())
    else:
        new_message = await channel.send(embed=embed, view=RegisterButton())
        await new_message.pin()
