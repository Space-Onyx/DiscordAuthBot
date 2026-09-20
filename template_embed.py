# Status embed config and static text
embed_status = {
    "color": 0x00ff00,
    "fields": [
        {"name": "Онлайн", "key": "online", "inline": True},
        {"name": "Карта", "key": "map", "inline": True},
        {"name": "Режим", "key": "preset", "inline": True},
        {"name": "Статус", "key": "status", "inline": True},
        {"name": "Время раунда", "key": "duration", "inline": True},
        {"name": "Раунд", "key": "round_id", "inline": True},
        {"name": "Бункер", "key": "bunker", "inline": True},
    ],
}

embed_log = {
    "title": "Использование команды",
    "color": 0x0099ff,
    "fields": [
        {"name": "Команда", "value": "ctx.command", "inline": False},
        {"name": "Пользователь", "value": "ctx.author", "inline": False},
        {"name": "ID пользователя", "value": "ctx.author.id", "inline": False},
        {"name": "Время", "value": "datetime.now().strftime('%Y-%m-%d %H:%M:%S')", "inline": False}
    ]
}

embed_admin_help = {
    "title": "Список админ-команд бота",
    "color": 0xFF0000,
    "description": "Префикс: `&`",
    "fields": [
        {"name": "Управление правами", "value": '&admin <nickname> — Проверка прав админа.\n&list_permission <server> — Выводит список прав сервера (по умолчанию БД-сервер по умолчанию).\n&add_permission <username> "<title>" "<permission>" <server> — Добавить права на выбранном сервере.\n&del_permission <username> <server> — Удалить права на выбранном сервере.\n&tweak_permission <username> "<title>" "<permission>" <server> — Изменить права на выбранном сервере.', "inline": False},
        {"name": "Информация об игроке", "value": '&playtime [ник|@пользователь] [--server имя] — Показывает общую и ролевую наигровку.\n&logs <username> <round> <server> — Ищет админ-логи за указанный раунд.\n&check_nick <nickname> <server> — Проверка на мультиаккаунт.\n&get_ckey <Discord id> — Получить ckey по ID дискорда.\n&notelist <nickname> <server> — Заметки игрока.\n&banlist <nickname> <server> — Банлист игрока.', "inline": False},
        {"name": "Баны и модерация", "value": '&ban <nickname> <reason...> <time_minutes> [server] — Выдает бан игроку.\n&kick <nickname> <reason...> [server] — Кик.\n&pardon <ban_id> [server] — Разбанивает игрока.\nПоддерживается явный сервер: --server <name> | -s <name> | server=<name>.', "inline": False},
        {"name": "Сервер", "value": '&servers — Список серверов, доступных боту.\n&status <server> — Информация о сервере.\n&admin_info <server> — Подробная информация о сервере.\n&bunker <on/off> <server> — Включает/выключает бункер.\n&update <server> — Запускает обновление сервера.\n&restart <server> — Перезапускает сервер.', "inline": False},
    ]
}

embed_list_permission = {
    "title": "Список прав",
    "color": 0xFF0000
}

embed_discord_link = {
    "title": "Привязка аккаунта SS14",
    "description": "Нажмите кнопку и введите временный код для привязки аккаунта SS14.",
    "color": 0x3498DB,
}

embed_help = {
    "title": "Список команд бота",
    "color": 0x0099ff,
    "fields": [
        {"name": "Основные команды", "value": '&help — Справка по командам.\n&whoami — Ваши привязки и общая наигровка по серверам.\n&playtime [сервер] — Ваша полная наигровка (`&hours` тоже работает).\n&servers — Доступные серверы.\n&status <сервер> — Статус игрового сервера.\n&user_role <роль> — Участники роли.', "inline": False},
        {"name": "Автоматизация", "value": 'Бот обновляет сообщения со статусом серверов, принимает игровые уведомления и управляет привязкой аккаунтов.', "inline": False},
        {"name": "Репозиторий", "value": 'https://github.com/Space-Onyx/DiscordAuthBot | Оригинальный автор: [Darkiich](https://github.com/Darkiich)', "inline": False}
    ]
}

# Уведомления о раундах из Round API сервера (Content.Server.Corvax.Api.Round).
# Пинг роли отправляется отдельным content вне embed.
embed_round = {
    "lobby": {
        "title": "Новый раунд начинается!",
        "color": 0xF1C40F,
    },
    "started": {
        "title": "Раунд начался",
        "color": 0x00FF00,
        "fields": [
            {"name": "Раунд", "key": "round_id", "inline": True},
            {"name": "Карта", "key": "map", "inline": True},
            {"name": "Режим", "key": "preset", "inline": True},
            {"name": "Онлайн", "key": "online", "inline": True},
        ],
    },
    "ended": {
        "title": "Раунд завершён",
        "color": 0xE74C3C,
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
    "color": 0x0099FF,
}

# Уведомления о банах из Ban API сервера (Content.Server._Onyx.Discord.Bans).
# Всегда только embed, без пинга. Цвет приходит с сервера.
embed_ban = {
    "color": 0x8B0000,
}
