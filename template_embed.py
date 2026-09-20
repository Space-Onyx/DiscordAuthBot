# Shared embed styles and static text.
COLOR_PRIMARY = 0xF15861
COLOR_SUCCESS = 0x57F287
COLOR_WARNING = 0xFEE75C
COLOR_DANGER = 0xED4245
COLOR_NEUTRAL = 0x2B2D31

embed_status = {
    "color": COLOR_PRIMARY,
    "fields": [
        {"name": "Игроки", "key": "online", "inline": True},
        {"name": "Карта", "key": "map", "inline": True},
        {"name": "Режим", "key": "preset", "inline": True},
        {"name": "Состояние", "key": "status", "inline": True},
        {"name": "Длительность", "key": "duration", "inline": True},
        {"name": "Раунд", "key": "round_id", "inline": True},
        {"name": "Паник-бункер", "key": "bunker", "inline": True},
    ],
}

embed_log = {
    "title": "Команда выполнена",
    "color": COLOR_NEUTRAL,
    "fields": [
        {"name": "Команда", "value": "ctx.command", "inline": True},
        {"name": "Пользователь", "value": "ctx.author", "inline": True},
        {"name": "Discord ID", "value": "ctx.author.id", "inline": True},
    ]
}

embed_admin_help = {
    "title": "Панель команд",
    "color": COLOR_DANGER,
    "description": "Префикс команд: `&`",
    "fields": [
        {"name": "Права", "value": '`&admin <ник>` — проверить права\n`&list_permission [сервер]` — доступные ранги\n`&add_permission <ник> "<титул>" "<ранг>" [сервер]`\n`&tweak_permission <ник> "<титул>" "<ранг>" [сервер]`\n`&del_permission <ник> [сервер]`', "inline": False},
        {"name": "Игроки", "value": '`&playtime [ник|@пользователь] [--server имя]`\n`&check_nick <ник> [сервер]` — связанные аккаунты\n`&get_ckey <Discord ID>` — игровая привязка\n`&notelist <ник> [сервер]` — заметки\n`&banlist <ник> [сервер]` — история банов\n`&logs <ник> <раунд> [сервер]` — админ-логи', "inline": False},
        {"name": "Модерация", "value": '`&ban <ник> <причина> <минуты> [сервер]`\n`&kick <ник> <причина> [сервер]`\n`&pardon <ban_id> [сервер]`', "inline": True},
        {"name": "Сервер", "value": '`&admin_info [сервер]`\n`&bunker <on|off> [сервер]`\n`&update [сервер]`\n`&restart [сервер]`', "inline": True},
        {"name": "Выбор сервера", "value": "Последний аргумент либо `--server <имя>`, `-s <имя>`, `server=<имя>`.", "inline": False},
    ]
}

embed_list_permission = {
    "title": "Административные ранги",
    "color": COLOR_DANGER
}

embed_discord_link = {
    "title": "Связать аккаунт SS14",
    "description": "Нажмите кнопку и укажите cKey и 12-значный код.",
    "color": COLOR_PRIMARY,
}

embed_help = {
    "title": "Команды бота",
    "color": COLOR_PRIMARY,
    "fields": [
        {"name": "Аккаунт", "value": '`&whoami` — ваши привязки и общая наигровка\n`&playtime [сервер]` — полная наигровка по ролям\nПсевдоним: `&hours`', "inline": False},
        {"name": "Серверы", "value": '`&servers` — доступные игровые серверы\n`&status [сервер]` — текущее состояние сервера', "inline": True},
        {"name": "Discord", "value": '`&user_role <роль>` — участники выбранной роли\n`&help` — открыть эту справку', "inline": True},
        {"name": "О проекте", "value": '[Исходный код бота](https://github.com/Space-Onyx/DiscordAuthBot)\nОригинальный автор: [Darkiich](https://github.com/Darkiich)', "inline": False}
    ]
}

# Уведомления о раундах из Round API сервера (Content.Server.Corvax.Api.Round).
# Пинг роли отправляется отдельным content вне embed.
embed_round = {
    "lobby": {
        "title": "Новый раунд",
        "color": COLOR_WARNING,
    },
    "started": {
        "title": "Раунд начался",
        "color": COLOR_SUCCESS,
        "fields": [
            {"name": "Раунд", "key": "round_id", "inline": True},
            {"name": "Карта", "key": "map", "inline": True},
            {"name": "Режим", "key": "preset", "inline": True},
            {"name": "Онлайн", "key": "online", "inline": True},
        ],
    },
    "ended": {
        "title": "Раунд завершён",
        "color": COLOR_DANGER,
        "fields": [
            {"name": "Раунд", "key": "round_id", "inline": True},
            {"name": "Длительность", "key": "duration", "inline": True},
            {"name": "Онлайн", "key": "online", "inline": True},
        ],
    },
}

# Уведомления об ахелпах из AHelp API сервера (Content.Server.Corvax.Api.AHelp).
# Пинг роли отправляется отдельным content вне embed только для новых обращений.
embed_ahelp = {
    "title": "Ахелп",
    "color": COLOR_PRIMARY,
}

# Уведомления о банах из Ban API сервера (Content.Server._Onyx.Discord.Bans).
# Всегда только embed, без пинга. Цвет приходит с сервера.
embed_ban = {
    "color": COLOR_DANGER,
}
