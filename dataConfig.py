import json
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

MAX_SERVERS = 5


# Единый набор ролей доступа для текущей конфигурации проекта.
PROJECT_ACCESS_ROLES = [
    1474158624166383748, # Руководство проекта
    1474158624136757530, # Глава разработки
    1474158624136757529, # Администрация
]

ROLE_ACCESS_HEADS = [
    1474158624166383748, # Руководство проекта
    1474158624136757530, # Глава разработки
    1474158624136757529, # Администрация
    1474158624136757523, # Куратор модерации
    1474158624136757522, # Куратор ивентологии
    1474158624136757521, # Куратор караула
]
ROLE_ACCESS_MAINTAINER = [
    1474158624166383748, # Руководство проекта
    1474158624136757530, # Глава разработки
    1474158624136757529, # Администрация
]
ROLE_ACCESS_ADMIN = [
    1474158624166383748, # Руководство проекта
    1474158624136757530, # Глава разработки
    1474158624136757529, # Администрация
    1474158624136757523, # Куратор модерации
    1474158624136757522, # Куратор ивентологии
    1474158624107532423, # Ведущий модератор
    1474158624053137437, # Старший модератор
    1474158624053137428, # Модератор
]
GENERAL_ACCESS = [
    1474158624166383748, # Руководство проекта
    1474158624136757530, # Глава разработки
    1474158624136757529, # Администрация
]
ROLE_ACCESS_DOWN_ADMIN = [
    1474158624166383748, # Руководство проекта
    1474158624136757530, # Глава разработки
    1474158624136757529, # Администрация
    1474158624136757523, # Куратор модерации
    1474158624136757522, # Куратор ивентологии

]
ROLE_ACCESS_OBSERVER_ADMIN = [
    1474158624166383748, # Руководство проекта
    1474158624136757530, # Глава разработки
    1474158624136757529, # Администрация
    1474158624136757523, # Куратор модерации
    1474158624136757522, # Куратор ивентологии
]
ROLE_ACCESS_DEPARTAMENT_OF_UNBAN_ADMIN = [
    1474158624166383748, # Руководство проекта
    1474158624136757530, # Глава разработки
    1474158624136757529, # Администрация
    1474158624136757523, # Куратор модерации
    1474158624136757522, # Куратор ивентологии
    1474158624107532423, # Ведущий модератор
    1474158624053137437, # Старший модератор
]
ROLE_ACCESS_TOP_HEADS = [
    1474158624166383748, # Руководство проекта
    1474158624136757530, # Глава разработки
    1474158624136757529, # Администрация
]


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


def get_env_bool(key: str, default: bool) -> bool:
    value = os.getenv(key)
    if value in (None, ""):
        return default

    normalized = value.strip().lower()
    return normalized in ("1", "true", "yes", "on")


def _normalize_server_name(value: str | None) -> str:
    return (value or "").strip().lower()


# Токен Discord-бота.
DISCORD_KEY = get_env("DISCORD_KEY")
# GitHub token для git-команд бота.
USER_KEY_GITHUB = get_env("USER_KEY_GITHUB")

POST_USER_AGENT = get_env_optional("POST_USER_AGENT") or "DiscordAuthBot/1.0"

# Discord-каналы
CHANNEL_AUTH_DISCORD = 1488907777941307453
CHANNEL_LOG_AUTH_DISCORD = 1488986067364348014
CHANNEL_STATUS_MESSAGE = 1488933475368042537

# API для запросов от SS14 (глобальная отвязка из игры через бота).
BOT_API_HOST = os.getenv("BOT_API_HOST", "127.0.0.1")
BOT_API_PORT = get_env_int("BOT_API_PORT", 8088)
BOT_API_TOKEN = get_env("BOT_API_TOKEN")

VACATION_ROLE_ID = 1474158624136757526
LINKED_ACCOUNT_ROLE_ID = None

# Данные администратора для API.
ADMIN_GUID = get_env("ADMIN_GUID")
ADMIN_NAME = get_env("ADMIN_NAME")
# Глобальный fallback токен admin API (можно переопределить на каждый сервер).
ADMIN_API = get_env_optional("ADMIN_API")

DATA_ADMIN = {
    "Guid": str(ADMIN_GUID),
    "Name": str(ADMIN_NAME),
}

LOG_CHANNEL_ID = 1488938774942715944
MY_DS_ID = 1488894891013443705


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
            )
        )

    return servers


def _load_legacy_servers() -> list[dict[str, Any]]:
    # Старый формат (astra/dev) — фолбэк для обратной совместимости.
    address_astra = os.getenv("ADDRESS_ASTRA", "109.195.84.233")
    address_dev = os.getenv("ADDRESS_DEV", "109.195.84.233")

    status_port_astra = get_env_int("STATUS_PORT_ASTRA", 1616)
    status_port_dev = get_env_int("STATUS_PORT_DEV", 1717)

    admin_api_port_astra = get_env_int("ADMIN_API_PORT_ASTRA", status_port_astra)
    admin_api_port_dev = get_env_int("ADMIN_API_PORT_DEV", status_port_dev)
    admin_api_token_astra = get_env_optional("ADMIN_API_TOKEN_ASTRA", ADMIN_API)
    admin_api_token_dev = get_env_optional("ADMIN_API_TOKEN_DEV", ADMIN_API)

    post_port_astra = get_env_int("POST_PORT_ASTRA", 5000)
    post_port_dev = get_env_int("POST_PORT_DEV", 5001)

    post_password_astra = get_env_optional("POST_PASSWORD_ASTRA")
    post_password_dev = get_env_optional("POST_PASSWORD_DEV")

    post_authorization_astra = get_env_optional("POST_AUTHORIZATION_ASTRA")
    post_authorization_dev = get_env_optional("POST_AUTHORIZATION_DEV")

    database_host_default = get_env_optional("DATABASE_HOST")
    database_port_default = get_env_optional("DATABASE_PORT")
    database_user_default = get_env_optional("DATABASE_USER")
    database_pass_default = get_env_optional("DATABASE_PASS")

    database_astra = get_env_optional("DATABASE_ASTRA")
    database_astra_host = get_env_optional("DATABASE_ASTRA_HOST", database_host_default)
    database_astra_port = get_env_optional("DATABASE_ASTRA_PORT", database_port_default)
    database_astra_user = get_env_optional("DATABASE_ASTRA_USER", database_user_default)
    database_astra_pass = get_env_optional("DATABASE_ASTRA_PASS", database_pass_default)

    database_dev = get_env_optional("DATABASE_DEV")
    database_dev_host = get_env_optional("DATABASE_DEV_HOST", database_host_default)
    database_dev_port = get_env_optional("DATABASE_DEV_PORT", database_port_default)
    database_dev_user = get_env_optional("DATABASE_DEV_USER", database_user_default)
    database_dev_pass = get_env_optional("DATABASE_DEV_PASS", database_pass_default)

    servers = [
        _build_server(
            name="astra",
            address=address_astra,
            status_port=status_port_astra,
            admin_api_port=admin_api_port_astra,
            admin_api_token=admin_api_token_astra,
            post_port=post_port_astra,
            post_instance="ASTRA",
            post_username="ASTRA",
            post_password=post_password_astra,
            post_authorization=post_authorization_astra,
            db_name=database_astra,
            db_host=database_astra_host,
            db_port=database_astra_port,
            db_user=database_astra_user,
            db_pass=database_astra_pass,
        ),
        _build_server(
            name="dev",
            address=address_dev,
            status_port=status_port_dev,
            admin_api_port=admin_api_port_dev,
            admin_api_token=admin_api_token_dev,
            post_port=post_port_dev,
            post_instance="DEV",
            post_username="DEV",
            post_password=post_password_dev,
            post_authorization=post_authorization_dev,
            db_name=database_dev,
            db_host=database_dev_host,
            db_port=database_dev_port,
            db_user=database_dev_user,
            db_pass=database_dev_pass,
        ),
    ]

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
if _dynamic_servers:
    _all_servers = _dedupe_servers(_dynamic_servers)[:MAX_SERVERS]
else:
    _all_servers = _dedupe_servers(_load_legacy_servers())[:MAX_SERVERS]

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

STATUS_MESSAGE_SERVER_NAME = _normalize_server_name(os.getenv("STATUS_MESSAGE_SERVER"))
if STATUS_MESSAGE_SERVER_NAME not in SERVERS:
    STATUS_MESSAGE_SERVER_NAME = DEFAULT_SERVER_NAME


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


# --- Совместимость со старыми импортами ---
ADDRESS_ASTRA = SERVERS.get("astra", {}).get("address", "")
ADDRESS_DEV = SERVERS.get("dev", {}).get("address", "")

DATA_ASTRA = build_post_data("astra") or {"Username": "ASTRA", "Password": None}
DATA_DEV = build_post_data("dev") or {"Username": "DEV", "Password": None}

HEADERS_ASTRA = build_post_headers("astra", DATA_ASTRA) or {}
HEADERS_DEV = build_post_headers("dev", DATA_DEV) or {}

POST_ADMIN_HEADERS = build_admin_headers(DEFAULT_SERVER_NAME) or {}
