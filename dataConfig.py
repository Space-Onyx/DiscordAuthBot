import json
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

MAX_SERVERS = 5


def _parse_role_list(key: str) -> list[int]:
    """Reads role lists directly from .env file to support multi-line, commented format."""
    import re
    
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        return []

    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = rf"{key}\s*=\s*\[(.*?)\]"
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        value = os.getenv(key)
        if not value:
            return []
        return [int(m) for m in re.findall(r'\d+', value)]
        
    block = match.group(1)
    return [int(m) for m in re.findall(r'\d+', block)]



PROJECT_ACCESS_ROLES = _parse_role_list("PROJECT_ACCESS_ROLES")
ROLE_ACCESS_HEADS = _parse_role_list("ROLE_ACCESS_HEADS")
ROLE_ACCESS_DEVELOPERS = _parse_role_list("ROLE_ACCESS_DEVELOPERS")
ROLE_ACCESS_MODERATORS = _parse_role_list("ROLE_ACCESS_MODERATORS")
ROLE_ACCESS_EVENTOLOGY = _parse_role_list("ROLE_ACCESS_EVENTOLOGY")
GENERAL_ACCESS = _parse_role_list("GENERAL_ACCESS")
ROLE_ACCESS_DOWN_ADMIN = _parse_role_list("ROLE_ACCESS_DOWN_ADMIN")
ROLE_ACCESS_OBSERVER_ADMIN = _parse_role_list("ROLE_ACCESS_OBSERVER_ADMIN")
ROLE_ACCESS_DEPARTAMENT_OF_UNBAN_ADMIN = _parse_role_list("ROLE_ACCESS_DEPARTAMENT_OF_UNBAN_ADMIN")
ROLE_ACCESS_TOP_HEADS = _parse_role_list("ROLE_ACCESS_TOP_HEADS")


def get_env(key: str):
    """Возвращает значение переменной окружения и пишет предупреждение, если ключ не найден."""
    env = os.getenv(key)
    if not env:
        print(f"Ключ секрета не найден: {key}")
    return env


def get_env_optional(key: str, default: str | None = None) -> str | None:
    value = os.getenv(key)
    if value in (None, ""):
        return default
    return value


def get_env_int(key: str, default: int) -> int:
    value = os.getenv(key)
    if value in (None, ""):
        return default

    try:
        return int(value)
    except ValueError:
        print(f"Некорректное число в {key}: {value}. Используется значение по умолчанию: {default}")
        return default


def get_required_env_int(key: str) -> int | None:
    value = get_env(key)
    if value in (None, ""):
        return None

    try:
        return int(value)
    except ValueError:
        print(f"Некорректное число в {key}: {value}.")
        return None


def get_env_bool(key: str, default: bool) -> bool:
    value = os.getenv(key)
    if value in (None, ""):
        return default

    normalized = value.strip().lower()
    return normalized in ("1", "true", "yes", "on")


def get_env_list(key: str) -> list[str]:
    value = os.getenv(key)
    if value in (None, ""):
        return []

    return [
        item.strip()
        for item in value.replace(";", ",").split(",")
        if item.strip()
    ]


def _normalize_server_name(value: str | None) -> str:
    return (value or "").strip().lower()


def _get_optional_env_int(key: str) -> int | None:
    value = get_env_optional(key)
    if value in (None, ""):
        return None

    try:
        return int(value)
    except ValueError:
        print(f"Некорректное число в {key}: {value}. Пропущено.")
        return None


# Токен Discord-бота.
DISCORD_KEY = get_env("DISCORD_KEY")
# GitHub token для git-команд бота.
USER_KEY_GITHUB = get_env_optional("USER_KEY_GITHUB")

POST_USER_AGENT = get_env_optional("POST_USER_AGENT") or "DiscordAuthBot/1.0"

# Discord-каналы
CHANNEL_AUTH_DISCORD = get_env_int("CHANNEL_AUTH_DISCORD", 0)
CHANNEL_LOG_AUTH_DISCORD = get_required_env_int("CHANNEL_LOG_AUTH_DISCORD")

# API для запросов от SS14 (глобальная отвязка из игры через бота).
BOT_API_HOST = os.getenv("BOT_API_HOST", "127.0.0.1")
BOT_API_PORT = get_env_int("BOT_API_PORT", 8088)
BOT_API_TOKEN = get_env("BOT_API_TOKEN")

VACATION_ROLE_ID = get_env("VACATION_ROLE_ID")
LINKED_ACCOUNT_ROLE_ID = get_env("LINKED_ACCOUNT_ROLE_ID")

# Данные администратора для API.
ADMIN_GUID = get_env("ADMIN_GUID")
ADMIN_NAME = get_env("ADMIN_NAME")
# Глобальный fallback токен admin API (можно переопределить на каждый сервер).
ADMIN_API = get_env_optional("ADMIN_API")

DATA_ADMIN = {
    "Guid": str(ADMIN_GUID),
    "Name": str(ADMIN_NAME),
}

LOG_CHANNEL_ID = get_required_env_int("LOG_CHANNEL_ID")
MY_DS_ID = get_env("MY_DS_ID")

# Ckeys whose IP/HWID matches should be hidden from &check_nick output.
CHECK_NICK_ACCOUNT_WHITELIST = {
    ckey.casefold()
    for ckey in get_env_list("CHECK_NICK_ACCOUNT_WHITELIST")
}


def _build_server(
    name: str,
    address: str,
    status_port: int,
    admin_api_port: int,
    admin_api_token: str | None,
    post_port: int,
    post_instance: str,
    post_username: str,
    post_password: str | None,
    post_authorization: str | None,
    db_name: str | None,
    db_host: str | None,
    db_port: str | None,
    db_user: str | None,
    db_pass: str | None,
    channel_auth_discord: int | None = None,
    round_channel: int | None = None,
    ahelp_channel: int | None = None,
    ban_channel: int | None = None,
    round_ping_role: int | None = None,
    ahelp_ping_role: int | None = None,
    game_host_name: str | None = None,
) -> dict[str, Any]:
    return {
        "name": _normalize_server_name(name),
        "display_name": (name or "").strip().upper(),
        "address": (address or "").strip(),
        "status_port": int(status_port),
        "admin_api_port": int(admin_api_port),
        "admin_api_token": admin_api_token,
        "post_port": int(post_port),
        "post_instance": (post_instance or name).strip().upper(),
        "post_username": (post_username or name).strip().upper(),
        "post_password": post_password,
        "post_authorization": post_authorization,
        "channel_auth_discord": channel_auth_discord,
        "round_channel": round_channel,
        "ahelp_channel": ahelp_channel,
        "ban_channel": ban_channel,
        "round_ping_role": round_ping_role,
        "ahelp_ping_role": ahelp_ping_role,
        "game_host_name": (game_host_name or "").strip(),
        "db": {
            "database": db_name,
            "host": db_host,
            "port": db_port,
            "user": db_user,
            "password": db_pass,
        }
    }


def _load_servers_from_slots() -> list[dict[str, Any]]:
    servers: list[dict[str, Any]] = []

    for idx in range(1, MAX_SERVERS + 1):
        prefix = f"SERVER_{idx}_"

        enabled = get_env_bool(f"{prefix}ENABLED", True)
        if not enabled:
            continue

        name = _normalize_server_name(get_env_optional(f"{prefix}NAME"))
        if not name:
            continue

        address = (get_env_optional(f"{prefix}ADDRESS") or "").strip()
        if not address:
            print(f"Сервер {name} пропущен: не указан {prefix}ADDRESS")
            continue

        status_port = get_env_int(f"{prefix}STATUS_PORT", 1616)
        admin_api_port = get_env_int(f"{prefix}ADMIN_API_PORT", status_port)
        admin_api_token = get_env_optional(f"{prefix}ADMIN_API_TOKEN", ADMIN_API)
        post_port = get_env_int(f"{prefix}POST_PORT", 5000)

        post_instance = get_env_optional(f"{prefix}POST_INSTANCE", name.upper())
        post_username = get_env_optional(f"{prefix}POST_USERNAME", name.upper())
        post_password = get_env_optional(f"{prefix}POST_PASSWORD")
        post_authorization = get_env_optional(f"{prefix}POST_AUTHORIZATION")

        db_name = get_env_optional(f"{prefix}DB_NAME")
        db_host = get_env_optional(f"{prefix}DB_HOST")
        db_port = get_env_optional(f"{prefix}DB_PORT")
        db_user = get_env_optional(f"{prefix}DB_USER")
        db_pass = get_env_optional(f"{prefix}DB_PASS")
        channel_auth_discord = get_env_int(f"{prefix}CHANNEL_AUTH_DISCORD", 0)
        if channel_auth_discord == 0:
            channel_auth_discord = None

        round_channel = _get_optional_env_int(f"{prefix}ROUND_CHANNEL")
        ahelp_channel = _get_optional_env_int(f"{prefix}AHELP_CHANNEL")
        ban_channel = _get_optional_env_int(f"{prefix}BAN_CHANNEL")
        round_ping_role = _get_optional_env_int(f"{prefix}ROUND_PING_ROLE")
        ahelp_ping_role = _get_optional_env_int(f"{prefix}AHELP_PING_ROLE")
        game_host_name = get_env_optional(f"{prefix}GAME_HOST_NAME")

        servers.append(
            _build_server(
                name=name,
                address=address,
                status_port=status_port,
                admin_api_port=admin_api_port,
                admin_api_token=admin_api_token,
                post_port=post_port,
                post_instance=post_instance or name.upper(),
                post_username=post_username or name.upper(),
                post_password=post_password,
                post_authorization=post_authorization,
                db_name=db_name,
                db_host=db_host,
                db_port=db_port,
                db_user=db_user,
                db_pass=db_pass,
                channel_auth_discord=channel_auth_discord,
                round_channel=round_channel,
                ahelp_channel=ahelp_channel,
                ban_channel=ban_channel,
                round_ping_role=round_ping_role,
                ahelp_ping_role=ahelp_ping_role,
                game_host_name=game_host_name,
            )
        )

    return servers



def _dedupe_servers(servers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []

    for server in servers:
        name = server.get("name", "")
        if not name or name in seen:
            continue
        seen.add(name)
        result.append(server)

    return result


def _db_configured(server: dict[str, Any]) -> bool:
    db = server.get("db") or {}
    required = ("database", "host", "port", "user", "password")
    return all((db.get(key) not in (None, "")) for key in required)


_dynamic_servers = _load_servers_from_slots()
_all_servers = _dedupe_servers(_dynamic_servers)[:MAX_SERVERS]

SERVERS: dict[str, dict[str, Any]] = {server["name"]: server for server in _all_servers}
SERVER_ORDER: list[str] = [server["name"] for server in _all_servers]

DEFAULT_SERVER_NAME = _normalize_server_name(os.getenv("DEFAULT_SERVER"))
if DEFAULT_SERVER_NAME not in SERVERS and SERVER_ORDER:
    DEFAULT_SERVER_NAME = SERVER_ORDER[0]

DB_SERVER_ORDER = [name for name in SERVER_ORDER if _db_configured(SERVERS[name])]
DATABASE_SERVERS = {
    name: {
        "database": SERVERS[name]["db"]["database"],
        "host": SERVERS[name]["db"]["host"],
        "port": SERVERS[name]["db"]["port"],
        "user": SERVERS[name]["db"]["user"],
        "password": SERVERS[name]["db"]["password"],
    }
    for name in DB_SERVER_ORDER
}

DEFAULT_DB_SERVER = _normalize_server_name(os.getenv("DEFAULT_DB_SERVER"))
if DEFAULT_DB_SERVER not in DATABASE_SERVERS:
    if DEFAULT_SERVER_NAME in DATABASE_SERVERS:
        DEFAULT_DB_SERVER = DEFAULT_SERVER_NAME
    elif DB_SERVER_ORDER:
        DEFAULT_DB_SERVER = DB_SERVER_ORDER[0]

def _parse_status_message_targets() -> list[tuple[str, int]]:
    targets: list[tuple[str, int]] = []
    for index, name in enumerate(SERVER_ORDER, start=1):
        key = f"SERVER_{index}_STATUS_CHANNEL"
        channel_id = get_env_optional(key)
        if channel_id in (None, ""):
            continue
        try:
            channel_int = int(channel_id)
        except ValueError:
            print(f"Некорректный канал статуса {key}: {channel_id}. Пропущено.")
            continue
        targets.append((name, channel_int))
    return targets

STATUS_MESSAGE_TARGETS = _parse_status_message_targets()

def get_status_message_targets() -> list[tuple[str, int]]:
    return STATUS_MESSAGE_TARGETS.copy()


def get_auth_channel_targets() -> list[tuple[str, int]]:
    targets: list[tuple[str, int]] = []
    for name in SERVER_ORDER:
        server = SERVERS.get(name)
        if server and server.get("channel_auth_discord"):
            targets.append((name, server["channel_auth_discord"]))
    if not targets and CHANNEL_AUTH_DISCORD:
        targets.append(("default", CHANNEL_AUTH_DISCORD))
    return targets


def get_server_names() -> list[str]:
    return SERVER_ORDER.copy()


def get_db_server_names() -> list[str]:
    return DB_SERVER_ORDER.copy()


def get_servers_text(db_required: bool = False) -> str:
    names = get_db_server_names() if db_required else get_server_names()
    return ", ".join(names) if names else "не настроены"


def resolve_server_name(server_name: str | None = None, db_required: bool = False) -> str | None:
    names = get_db_server_names() if db_required else get_server_names()
    if not names:
        return None

    if not server_name:
        if db_required:
            return DEFAULT_DB_SERVER or names[0]
        return DEFAULT_SERVER_NAME or names[0]

    normalized = _normalize_server_name(server_name)
    if normalized in names:
        return normalized

    return None


def get_server(server_name: str | None = None) -> dict[str, Any] | None:
    resolved = resolve_server_name(server_name, db_required=False)
    if not resolved:
        return None
    return SERVERS.get(resolved)


def get_db_server_config(server_name: str | None = None) -> dict[str, Any] | None:
    resolved = resolve_server_name(server_name, db_required=True)
    if not resolved:
        return None
    return DATABASE_SERVERS.get(resolved)


def resolve_server_by_host_name(host_name: str | None) -> dict[str, Any] | None:
    """Ищет конфиг сервера по GameHostName из push-событий SS14 (round/ahelp API)."""
    normalized = (host_name or "").strip().lower()
    if not normalized:
        return None

    for name in SERVER_ORDER:
        server = SERVERS[name]
        candidates = {
            (server.get("game_host_name") or "").strip().lower(),
            server.get("name", ""),
            (server.get("display_name") or "").strip().lower(),
            (server.get("post_instance") or "").strip().lower(),
        }
        candidates.discard("")
        if normalized in candidates:
            return server

    return None


def get_round_notify_target(host_name: str | None) -> tuple[dict[str, Any], int, int | None] | None:
    server = resolve_server_by_host_name(host_name)
    if not server or not server.get("round_channel"):
        return None
    return server, server["round_channel"], server.get("round_ping_role")


def get_ahelp_notify_target(host_name: str | None) -> tuple[dict[str, Any], int, int | None] | None:
    server = resolve_server_by_host_name(host_name)
    if not server or not server.get("ahelp_channel"):
        return None
    return server, server["ahelp_channel"], server.get("ahelp_ping_role")


def get_ban_notify_target(host_name: str | None) -> tuple[dict[str, Any], int] | None:
    server = resolve_server_by_host_name(host_name)
    if not server or not server.get("ban_channel"):
        return None
    return server, server["ban_channel"]


def build_status_url(server_name: str | None = None) -> str | None:
    server = get_server(server_name)
    if not server:
        return None
    return f"http://{server['address']}:{server['status_port']}/status"


def build_admin_url(path: str, server_name: str | None = None) -> str | None:
    server = get_server(server_name)
    if not server:
        return None

    route = path if path.startswith("/") else f"/{path}"
    return f"http://{server['address']}:{server['admin_api_port']}{route}"


def build_admin_headers(
    server_name: str | None = None,
    actor_data: dict[str, Any] | None = None,
) -> dict[str, str] | None:
    server = get_server(server_name)
    if not server:
        return None

    token = (server.get("admin_api_token") or "").strip()
    if not token:
        return None

    actor = actor_data or DATA_ADMIN
    headers = {
        "Authorization": f"SS14Token {token}",
        "Content-Type": "application/json",
    }

    if actor:
        headers["Actor"] = json.dumps(actor)

    return headers


def build_update_url(server_name: str | None = None) -> str | None:
    server = get_server(server_name)
    if not server:
        return None

    return f"http://{server['address']}:{server['post_port']}/instances/{server['post_instance']}/update"


def build_restart_url(server_name: str | None = None) -> str | None:
    server = get_server(server_name)
    if not server:
        return None

    return f"http://{server['address']}:{server['post_port']}/instances/{server['post_instance']}/restart"


def build_post_data(server_name: str | None = None) -> dict[str, Any] | None:
    server = get_server(server_name)
    if not server:
        return None

    return {
        "Username": server["post_username"],
        "Password": server["post_password"]
    }


def build_post_headers(server_name: str | None = None, data: dict[str, Any] | None = None) -> dict[str, str] | None:
    server = get_server(server_name)
    if not server:
        return None

    headers: dict[str, str] = {
        "Host": f"{server['address']}:{server['post_port']}",
        "User-Agent": POST_USER_AGENT,
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }

    authorization = server.get("post_authorization")
    if authorization:
        headers["Authorization"] = authorization

    return headers
