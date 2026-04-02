embed_status = {
    "title": "data.get('name', 'Без названия')",
    "color": 0x00ff00,
    "fields": [
        {"name": "Онлайн", "value": "f\"{data.get('players', 0)}/{data.get('soft_max_players', 0)}\"", "inline": True},
        {"name": "Карта", "value": "data.get('map', 'Неизвестно')", "inline": True},
        {"name": "Режим", "value": "data.get('preset', 'Неизвестно')", "inline": True},
        {"name": "Статус", "value": "status_text", "inline": True},
        {"name": "Раунд идёт", "value": "round_length_text", "inline": True},
        {"name": "Раунд", "value": "data.get('round_id', '—')", "inline": True},
        {"name": "Бункер", "value": "'Включен' if data.get('panic_bunker') else 'Выключен'", "inline": True}
    ]
}
embed_log = {
    "title": "Использование команды",
    "color": 0x0099ff,
    "fields": [
        {"name": "Команда", "value": "ctx.command", "inline": False},
        {"name": "Пользователь", "value": "ctx.author", "inline": False},
        {"name": "ID пользователя", "value": "ctx.author.id", "inline": False},
        {"name": "Время", "value": "datetime.now().strftime('%Y-%m-%d %H:%M:%S')", "inline": False},
        {"name": "Использованная команда", "value": "ctx.message.jump_url", "inline": False}
    ]
}

embed_publish_status = {
    "title": "Статус workflow publish-public.yml",
    "fields": [
        {"name": "Статус", "value": "translated_status", "inline": False},
        {"name": "Ветка", "value": "branch", "inline": False},
        {"name": "Пользователь", "value": "user", "inline": False}
    ]
}

embed_repoinfo = {
    "title": "Общая информация о репозитории space_station_ADT",
    "description": "data['description']",
    "color": 0x00ff00,
    "fields": [
        {"name": "Звёзды", "value": "str(data['stargazers_count'])", "inline": False},
        {"name": "Форки", "value": "str(data['forks_count'])", "inline": False},
        {"name": "Issues", "value": "str(data['open_issues_count'])", "inline": False},
        {"name": "Открытые PR", "value": "str(pr_count)", "inline": False},
        {"name": "Контрибьютеры", "value": "str(contrib_count)", "inline": False},
        {"name": "Создан", "value": "data['created_at'][:10]", "inline": False},
        {"name": "Обновлён", "value": "data['updated_at'][:10]", "inline": False},
        {"name": "Ссылка", "value": "data['html_url']", "inline": False}
    ]
}

embed_git_team = {
    "title": "Участники организации AdventureTimeSS14",
    "color": 0x00ff00,
    "fields": [
        {"name": "Участники", "value": "'\\n'.join([m['login'] for m in members]) or 'Нет'", "inline": False}
    ]
}

embed_branch = {
    "title": "Ветки репозитория space_station_ADT",
    "color": 0x00ff00,
    "fields": [
        {"name": "Ветки", "value": "'\\n\\n'.join([b['name'] for b in branches]) or 'Нет веток'", "inline": False}
    ]
}

embed_git_invite = {
    "title": "Результат приглашения в организацию AdventureTimeSS14",
    "color": 0x00ff00,
    "fields": [
        {"name": "Пользователь", "value": "username", "inline": False},
        {"name": "Статус", "value": "result", "inline": False}
    ]
}

embed_git_remove = {
    "title": "Результат удаления из организации AdventureTimeSS14",
    "color": 0x00ff00,
    "fields": [
        {"name": "Пользователь", "value": "username", "inline": False},
        {"name": "Статус", "value": "result", "inline": False}
    ]
}

embed_git_help = {
    "title": "Список Git-команд бота",
    "color": 0x0099ff,
    "description": "Префикс: `&`",
    "fields": [
        {"name": "&publish <branch>. По умолчанию master", "value": "Отправляет запрос на паблиш ветки.", "inline": False},
        {"name": "&publish_status", "value": "Показывает статус последнего запуска GitHub Actions workflow publish-adt.yml.", "inline": False},
        {"name": "&update <server>", "value": "Обновляет выбранный сервер (если не указан — сервер по умолчанию).", "inline": False},
        {"name": "&restart <server>", "value": "Перезагружает выбранный сервер (если не указан — сервер по умолчанию).", "inline": False},
        {"name": "&git_repoinfo", "value": "Показывает информацию о репозитории.", "inline": False},
        {"name": "&git_team", "value": "Показывает участников организации AdventureTimeSS14.", "inline": False},
        {"name": "&git_invite <username>", "value": "Приглашает пользователя в организацию.", "inline": False},
        {"name": "&git_remove <username>", "value": "Удаляет пользователя из организации.", "inline": False},
        {"name": "&add_maint <username>", "value": "Добавляет участника в команду adt_maintainer.", "inline": False},
        {"name": "&del_maint <username>", "value": "Удаляет участника из команды adt_maintainer.", "inline": False},
        {"name": "&branch", "value": "Показывает список веток репозитория.", "inline": False},
    ]
}

embed_admin_info = {
    "title": "Информация о сервере SS14",
    "color": 0x3498db,
    "fields": [
        {"name": "ID Раунда", "value": 'data.get("RoundId", "Не задано")', "inline": False},
        {"name": "Название карты", "value": 'data.get("Map", {}).get("Name", "Не задано")', "inline": False},
        {"name": "MOTD", "value": 'data.get("MOTD", "Нет сообщения")', "inline": False},
        {"name": "Геймпресет", "value": 'data.get("GamePreset", "Не задано")', "inline": False},
        {"name": "Игроки", "value": '"\\n".join([f"{p.get(\"Name\", \"?\")} - {\"Админ\" if p.get(\"IsAdmin\") else \"Игрок\"} ({p.get(\"PingUser\", \"?\")} ms)" for p in data.get("Players", []) if not p.get("IsDeadminned")]) or "Нет игроков"', "inline": False},
        {"name": "Деадмины", "value": '"\\n".join([f"{p.get(\"Name\", \"?\")} ({p.get(\"PingUser\", \"?\")} ms)" for p in data.get("Players", []) if p.get("IsDeadminned")]) or "Нет"', "inline": False},
        {"name": "Активные админы", "value": '"\\n".join([f"{p.get(\"Name\", \"?\")}" for p in data.get("Players", []) if p.get("IsAdmin") and not p.get("IsDeadminned")]) or "Нет"', "inline": False},
        {"name": "Правила игры", "value": '"\\n".join(data.get("GameRules", [])) or "Нет правил"', "inline": False},
        {"name": "Panic Bunker", "value": '"\\n".join([f"{k}: {v}" for k, v in data.get("PanicBunker", {}).items() if v is not None]) or "Не активирован"', "inline": False},
    ]
}

embed_admin_help = {
    "title": "Список админ-команд бота",
    "color": 0xFF0000,
    "description": "Префикс: `&`",
    "fields": [
        {"name": "Управление правами", "value": '&admin <nickname> — Проверка прав админа.\n&list_permission <server> — Выводит список прав сервера (по умолчанию БД-сервер по умолчанию).\n&add_permission <username> \"<title>\" \"<permission>\" <server> — Добавить права на выбранном сервере.\n&del_permission <username> <server> — Удалить права на выбранном сервере.\n&tweak_permission <username> \"<title>\" \"<permission>\" <server> — Изменить права на выбранном сервере.', "inline": False},
        {"name": "Информация о игроке", "value": '&logs <username> <round> <server> — Ищет админ-логи за указанный раунд.\n&check_nick <nickname> <server> — Проверка на мультиаккаунт.\n&get_ckey <Discord id> — Получить ckey по ID дискорда.\n&notelist <nickname> <server> — Заметки игрока.\n&banlist <nickname> <server> — Банлист игрока.', "inline": False},
        {"name": "Баны и модерация", "value": '&ban <nickname> \"<reason>\" <time> в минутах — Выдает бан игроку.\n&kick <nickname> \"<reason>\" — Кик.\n&pardon <ban_id> — Разбанивает игрока.', "inline": False},
        {"name": "Сервер", "value": '&servers — Список серверов, доступных боту.\n&status <server> — Информация о сервере.\n&admin_info <server> — Подробная информация о сервере.\n&bunker <on/off> <server> — Включает/выключает бункер.', "inline": False},
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
        {"name": "Основные команды", "value": '🤖 &help — Вывод всех команд бота.\n😈 &admin_help — Вывод админ-команд для взаимодействия с игровым сервером.\n🔍 &check — Проверяет работу бота.\n🎭 &user_role <роль> — Выводит список пользователей с этой ролью.\n🧭 &servers — Показывает серверы, доступные боту.\n🎮 &status <server> — Выводит информацию о выбранном игровом сервере.', "inline": False},
        {"name": "\nЧто ещё умеет бот:", "value": '📢 Обновлять статус сервера в канале #https://discord.com/channels/1474158623834898648/1488933475368042537\n📖 Обновлять список команды проекта в указаном канале.', "inline": False},
        {"name": "\nРепозиторий бота:", "value": '🔗 Гитхаб: https://github.com/Space-Onyx/DiscordAuthBot | Оригинальный автор: [Darkiich](https://github.com/Darkiich)', "inline": False}
    ]
}



