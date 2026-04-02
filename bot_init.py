from disnake import Intents
from disnake.ext.commands import Bot
from AHelperManager.database_ss14 import DatabaseManagerSS14

# Minimal intents required for prefix commands and guild operations.
# This avoids requesting unnecessary privileged intents from Intents.all().
intent = Intents.default()
intent.message_content = True
intent.guilds = True
intent.guild_messages = True
intent.guild_reactions = True

bot = Bot(
    help_command=None,
    command_prefix="&",
    intents=intent
)

ss14_db = DatabaseManagerSS14()
