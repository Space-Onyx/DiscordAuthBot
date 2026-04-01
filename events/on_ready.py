from bot_init import bot
from tasks.discord_auth import RegisterButton, discord_auth_update, linked_role_sync_task, sync_linked_account_roles
from tasks.team_list import list_team_task
from tasks.status_message import status_update


@bot.event
async def on_ready():
    bot.add_view(RegisterButton())
    if not discord_auth_update.is_running():
        discord_auth_update.start()
    if not list_team_task.is_running():
        list_team_task.start()
    if not status_update.is_running():
        status_update.start()
    if not linked_role_sync_task.is_running():
        linked_role_sync_task.start()

    try:
        await sync_linked_account_roles()
    except Exception as e:
        print(f"[on_ready] Linked role initial sync skipped: {e}")
