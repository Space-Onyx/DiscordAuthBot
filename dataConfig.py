import os
import json

from dotenv import load_dotenv

load_dotenv()

# Единый набор ролей доступа для текущей конфигурации проекта.
# 1474158624166383748 - Руководство проекта
# 1474158624136757530 - Главный разработчик
# 1474158624136757529 - Администрация
PROJECT_ACCESS_ROLES = [
    1474158624166383748,
    1474158624136757530,
    1474158624136757529,
]

ROLE_ACCESS_HEADS = PROJECT_ACCESS_ROLES.copy()
ROLE_ACCESS_MAINTAINER = PROJECT_ACCESS_ROLES.copy()
ROLE_ACCESS_ADMIN = PROJECT_ACCESS_ROLES.copy()
GENERAL_ACCESS = PROJECT_ACCESS_ROLES.copy()
ROLE_ACCESS_DOWN_ADMIN = PROJECT_ACCESS_ROLES.copy()
ROLE_ACCESS_OBSERVER_ADMIN = PROJECT_ACCESS_ROLES.copy()
ROLE_ACCESS_DEPARTAMENT_OF_UNBAN_ADMIN = PROJECT_ACCESS_ROLES.copy()
ROLE_ACCESS_TOP_HEADS = PROJECT_ACCESS_ROLES.copy()


def get_env(key: str):
    """Возвращает значение переменной окружения и пишет предупреждение, если ключ не найден."""
    env = os.getenv(key)
    if not env:
        print(f"Ключ секрета не найден: {key}")
    return env


# Токен Discord-бота.
DISCORD_KEY = get_env("DISCORD_KEY")
# GitHub token для git-команд бота.
USER_KEY_GITHUB = get_env("USER_KEY_GITHUB")

# ВНИМАНИЕ: POST-часть не трогаем (по запросу), оставлено как было.
ADDRESS_ASTRA = "109.195.84.233"
ADDRESS_DEV = "109.195.84.233"

POST_PASSWORD_ASTRA = get_env("POST_PASSWORD_ASTRA")
POST_PASSWORD_DEV = get_env("POST_PASSWORD_DEV")

POST_AUTHORIZATION_ASTRA = get_env("POST_AUTHORIZATION_ASTRA")
POST_AUTHORIZATION_DEV = get_env("POST_AUTHORIZATION_DEV")

POST_USER_AGENT = get_env("POST_USER_AGENT")

# Discord каналы
CHANNEL_AUTH_DISCORD = 1488741685579088060
CHANNEL_LOG_AUTH_DISCORD = 1488892442819428445
CHANNEL_STATUS_MESSAGE = 1488741442787606769

VACATION_ROLE_ID = 1474158624136757526

# Данные администратора для API (POST-часть).
ADMIN_GUID = get_env("ADMIN_GUID")
ADMIN_NAME = get_env("ADMIN_NAME")
ADMIN_API = get_env("ADMIN_API")

# --- Базы данных SS14 ---
# Astra (основной сервер)
DATABASE_ASTRA = get_env("DATABASE_ASTRA")
DATABASE_ASTRA_HOST = os.getenv("DATABASE_ASTRA_HOST") or get_env("DATABASE_HOST")
DATABASE_ASTRA_PORT = os.getenv("DATABASE_ASTRA_PORT") or get_env("DATABASE_PORT")
DATABASE_ASTRA_USER = os.getenv("DATABASE_ASTRA_USER") or get_env("DATABASE_USER")
DATABASE_ASTRA_PASS = os.getenv("DATABASE_ASTRA_PASS") or get_env("DATABASE_PASS")

# Dev (тестовый сервер)
DATABASE_DEV = get_env("DATABASE_DEV")
DATABASE_DEV_HOST = os.getenv("DATABASE_DEV_HOST") or get_env("DATABASE_HOST")
DATABASE_DEV_PORT = os.getenv("DATABASE_DEV_PORT") or get_env("DATABASE_PORT")
DATABASE_DEV_USER = os.getenv("DATABASE_DEV_USER") or get_env("DATABASE_USER")
DATABASE_DEV_PASS = os.getenv("DATABASE_DEV_PASS") or get_env("DATABASE_PASS")

LOG_CHANNEL_ID = 1488741685579088060
MY_DS_ID = 1474158624136757530

VALENTINE_IMAGE_PATH = "src/valentine_card/image_valentine.png"

# ВНИМАНИЕ: POST-часть не трогаем (по запросу), оставлено как было.
DATA_ASTRA = {
    "Username": "ASTRA",
    "Password": POST_PASSWORD_ASTRA
}

HEADERS_ASTRA = {
    "Authorization": POST_AUTHORIZATION_ASTRA,
    "Content-Length": str(len(DATA_ASTRA)),
    "Host": f"{ADDRESS_ASTRA}:5000",
    "User-Agent": POST_USER_AGENT,
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

DATA_DEV = {
    "Username": "DEV",
    "Password": POST_PASSWORD_DEV
}

HEADERS_DEV = {
    "Authorization": POST_AUTHORIZATION_DEV,
    "Content-Length": str(len(DATA_DEV)),
    "Host": f"{ADDRESS_DEV}:5001",
    "User-Agent": POST_USER_AGENT,
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

DATA_ADMIN = {
    "Guid": str(ADMIN_GUID),
    "Name": str(ADMIN_NAME)
}

POST_ADMIN_HEADERS = {
    "Authorization": f"SS14Token {ADMIN_API}",
    "Content-Type": "application/json",
    "Actor": json.dumps(DATA_ADMIN)
}
