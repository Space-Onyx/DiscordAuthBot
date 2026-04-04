from dataConfig import get_servers_text, resolve_server_name


def resolve_server_for_command(server_arg: str | None = None, db_required: bool = False) -> tuple[str | None, str | None]:
    resolved = resolve_server_name(server_arg, db_required=db_required)
    if resolved:
        return resolved, None

    available = get_servers_text(db_required=db_required)
    if db_required:
        return None, f"Неверный сервер БД. Доступные: {available}"

    return None, f"Неверный сервер. Доступные: {available}"


def parse_server_from_tokens(
    tokens: tuple[str, ...] | list[str] | None,
    *,
    db_required: bool = False,
    trailing_server_min_tokens: int = 2,
) -> tuple[list[str], str | None, str | None]:
    """
    Возвращает (cleaned_tokens, resolved_server_name, error).
    Поддерживаемые форматы:
    - --server <name>
    - -s <name>
    - server=<name>
    - srv=<name>
    - <name> последним аргументом (если распознан как сервер)
    """
    raw_tokens = [str(token).strip() for token in (tokens or ()) if str(token).strip()]
    explicit_server: str | None = None
    cleaned_tokens: list[str] = []

    i = 0
    while i < len(raw_tokens):
        token = raw_tokens[i]
        lowered = token.lower()

        if lowered in ("--server", "-s"):
            if i + 1 >= len(raw_tokens):
                return [], None, "После --server укажите имя сервера."

            explicit_server = raw_tokens[i + 1]
            i += 2
            continue

        if lowered.startswith("server=") or lowered.startswith("srv="):
            _, value = token.split("=", 1)
            value = value.strip()
            if not value:
                return [], None, "После server= укажите имя сервера."

            explicit_server = value
            i += 1
            continue

        cleaned_tokens.append(token)
        i += 1

    if explicit_server is None and len(cleaned_tokens) >= trailing_server_min_tokens:
        trailing_server = cleaned_tokens[-1]
        if resolve_server_name(trailing_server, db_required=db_required):
            explicit_server = trailing_server
            cleaned_tokens = cleaned_tokens[:-1]

    server_name, error = resolve_server_for_command(explicit_server, db_required=db_required)
    if error:
        return [], None, error

    return cleaned_tokens, server_name, None
