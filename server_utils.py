from dataConfig import get_servers_text, resolve_server_name


def resolve_server_for_command(server_arg: str | None = None, db_required: bool = False) -> tuple[str | None, str | None]:
    resolved = resolve_server_name(server_arg, db_required=db_required)
    if resolved:
        return resolved, None

    available = get_servers_text(db_required=db_required)
    if db_required:
        return None, f"Неверный сервер БД. Доступные: {available}"

    return None, f"Неверный сервер. Доступные: {available}"
