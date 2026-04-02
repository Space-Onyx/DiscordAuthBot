import asyncpg
import asyncio
import re
from dataConfig import (
    DATABASE_SERVERS,
    DB_SERVER_ORDER,
    DEFAULT_DB_SERVER,
)
from datetime import datetime

LINK_CODE_REGEX = re.compile(r"^[0-9A-F]{9}$")


class _PoolConnWrapper:
    def __init__(self, conn: asyncpg.Connection, pool: asyncpg.Pool):
        self._conn = conn
        self._pool = pool
        self._closed = False

    def __getattr__(self, item):
        return getattr(self._conn, item)

    async def close(self):
        if self._closed:
            return
        self._closed = True
        await self._pool.release(self._conn)

class DatabaseManagerSS14:
    """
    Класс для работы в БД SS14
    """
    def __init__(self):
        self.db_params = {name: params.copy() for name, params in DATABASE_SERVERS.items()}
        self.db_order = DB_SERVER_ORDER.copy()
        self.default_db_name = DEFAULT_DB_SERVER
        self._pools: dict[str, asyncpg.Pool] = {}
        self._pool_locks: dict[str, asyncio.Lock] = {}
        self._command_timeout = 10

    def _get_pool_lock(self, db_name: str) -> asyncio.Lock:
        lock = self._pool_locks.get(db_name)
        if lock is None:
            lock = asyncio.Lock()
            self._pool_locks[db_name] = lock
        return lock

    def _is_db_configured(self, db_name: str) -> bool:
        params = self.db_params.get(db_name)
        if not params:
            return False
        required = ('database', 'user', 'password', 'host', 'port')
        return all(params.get(key) not in (None, '') for key in required)

    def _linked_lookup_order(self, db_name: str | None = None) -> list[str]:
        configured = [db for db in self.db_order if self._is_db_configured(db)]
        if not configured:
            return []

        preferred = (db_name or self.default_db_name or "").strip().lower()
        if preferred and preferred in configured:
            return [preferred] + [db for db in configured if db != preferred]

        return configured

    async def get_connection(self, db_name: str | None = None):
        """Возвращает асинхронное соединение с указанной базой данных"""
        target_db = (db_name or self.default_db_name or "").strip().lower()

        if target_db not in self.db_params:
            if self.default_db_name and self.default_db_name in self.db_params:
                target_db = self.default_db_name
            else:
                raise ValueError(f"Неизвестное имя БД: {db_name}")

        if not self._is_db_configured(target_db):
            raise ValueError(f"БД {target_db} не настроена")

        params = self.db_params[target_db]
        dsn = f"postgres://{params['user']}:{params['password']}@{params['host']}:{params['port']}/{params['database']}"
        pool = self._pools.get(target_db)
        if pool is None:
            lock = self._get_pool_lock(target_db)
            async with lock:
                pool = self._pools.get(target_db)
                if pool is None:
                    pool = await asyncpg.create_pool(
                        dsn,
                        min_size=1,
                        max_size=10,
                        command_timeout=self._command_timeout,
                    )
                    self._pools[target_db] = pool
        conn = await pool.acquire()
        return _PoolConnWrapper(conn, pool)

    async def get_admin_name(self, guid: str, db_name: str = 'astra'):
        """
        Получает имя администратора по GUID.
        """
        conn = await self.get_connection(db_name)
        try:
            result = await conn.fetchval("SELECT last_seen_user_name FROM player WHERE user_id = $1", guid)
            return result if result else None
        finally:
            await conn.close()

    async def get_player_guid(self, nickname: str, db_name: str = 'astra'):
        """
        Получает GUID игрока по имени.
        """
        conn = await self.get_connection(db_name)
        try:
            result = await conn.fetchval("SELECT user_id FROM player WHERE last_seen_user_name = $1", nickname)
            return result if result else None
        finally:
            await conn.close()

    async def get_player_guid_by_discord_id(self, ds_id: str, db_name: str = 'astra'):
        """
        Получает GUID игрока по ID дискорда.
        """
        last_error = None
        for current_db in self._linked_lookup_order(db_name):
            conn = None
            try:
                conn = await self.get_connection(current_db)
                result = await conn.fetchval("SELECT user_id FROM discord_user WHERE discord_id = $1", ds_id)
                if result:
                    return result
            except Exception as e:
                last_error = e
            finally:
                if conn:
                    await conn.close()
        if last_error:
            print(f"Ошибка поиска привязки discord_id={ds_id}: {last_error}")
        return None
    
    async def get_discord_info_by_guid(self, user_id: str, db_name: str = 'astra'):
        """
        Получает discord id по GUID пользователя.
        """
        last_error = None
        for current_db in self._linked_lookup_order(db_name):
            conn = None
            try:
                conn = await self.get_connection(current_db)
                result = await conn.fetchval("SELECT discord_id FROM discord_user WHERE user_id = $1", user_id)
                if result:
                    return result
            except Exception as e:
                last_error = e
            finally:
                if conn:
                    await conn.close()
        if last_error:
            print(f"Ошибка поиска discord_id по user_id={user_id}: {last_error}")
        return None

    async def get_player_name(self, guid: str, db_name: str = 'astra'):
        """
        Получает имя игрока по GUID.
        """
        conn = await self.get_connection(db_name)
        try:
            result = await conn.fetchval("SELECT last_seen_user_name FROM player WHERE user_id = $1", guid)
            return result if result else None
        finally:
            await conn.close()

    async def search_ban_player(self, username: str, db_name: str = 'astra'):
        """
        Получает историю банов игрока по нику.
        """
        conn = await self.get_connection(db_name)
        try:
            result = await conn.fetch("""
                SELECT 
                    sb.server_ban_id, 
                    sb.ban_time, 
                    sb.expiration_time, 
                    sb.reason, 
                    COALESCE(p.last_seen_user_name, 'Неизвестно') AS admin_nickname,
                    ub.unban_time,
                    COALESCE(p2.last_seen_user_name, 'Неизвестно') AS unban_admin_nickname
                FROM server_ban sb
                LEFT JOIN player p ON sb.banning_admin = p.user_id
                LEFT JOIN server_unban ub ON sb.server_ban_id = ub.ban_id
                LEFT JOIN player p2 ON ub.unbanning_admin = p2.user_id
                WHERE sb.player_user_id = (
                    SELECT user_id FROM player WHERE last_seen_user_name = $1
                )
                ORDER BY sb.server_ban_id ASC
            """, username)
            return result
        except Exception as e:
            print(f"Ошибка БД: {e}")
            return None
        finally:
            await conn.close()

    async def search_notes_player(self, username: str, db_name: str = 'astra'):
        """
        Получает заметки игрока по нику.
        """
        conn = await self.get_connection(db_name)
        try:
            result = await conn.fetch("""
                SELECT 
                    admin_notes.admin_notes_id,
                    admin_notes.created_at,
                    admin_notes.message,
                    admin_notes.severity,
                    admin_notes.secret,
                    admin_notes.last_edited_at,
                    admin_notes.last_edited_by_id,
                    player.player_id,
                    player.last_seen_user_name,
                    admin.created_by_name
                FROM admin_notes
                INNER JOIN player ON admin_notes.player_user_id = player.user_id
                LEFT JOIN (
                    SELECT user_id AS created_by_id, last_seen_user_name AS created_by_name
                    FROM player
                ) AS admin ON admin_notes.created_by_id = admin.created_by_id
                WHERE player.last_seen_user_name = $1
            """, username)
            return result
        except Exception as e:
            print(f"Ошибка БД: {e}")
            return None
        finally:
            await conn.close()

    async def unban_player(self, ban_id: int, admin_guid: str, unban_time, db_name: str = 'astra'):
        conn = await self.get_connection(db_name)
        try:
            async with conn.transaction():
                exists = await conn.fetchval("SELECT 1 FROM server_ban WHERE server_ban_id = $1", ban_id)
                if not exists:
                    return False, f"❌ Бан {ban_id} не существует."

                already_unbanned = await conn.fetchval("SELECT 1 FROM server_unban WHERE ban_id = $1", ban_id)
                if already_unbanned:
                    return False, f"⚠️ Бан {ban_id} уже снят."

                admin_name = await self.get_admin_name(admin_guid, db_name)
                if not admin_name:
                    return False, f"❌ При попытке найти имя админа в БД произошла ошибка: Админ с GUID {admin_guid} не найден."

                await conn.execute("""
                    INSERT INTO server_unban (ban_id, unbanning_admin, unban_time)
                    VALUES ($1, $2, $3::timestamptz)
                """, ban_id, admin_guid, unban_time)

                return True, f"✅ Бан {ban_id} снят админом {admin_name}."
        except Exception as e:
            return False, f"Ошибка: {e}"
        finally:
            await conn.close()
    
    async def get_admin_permission(self, nickname: str, db_name: str = 'astra'):
        conn = await self.get_connection(db_name)
        try:
            result = await conn.fetchrow("""
                SELECT a.title, ar.name
                FROM admin a
                JOIN admin_rank ar ON a.admin_rank_id = ar.admin_rank_id
                JOIN player p ON a.user_id = p.user_id
                WHERE p.last_seen_user_name ILIKE $1
            """, nickname)
            return result
        finally:
            await conn.close()

    async def get_all_player_info(self, user_name: str, db_name: str = 'astra'):
        conn = await self.get_connection(db_name)
        try:
            result = await conn.fetchrow("""
                SELECT player_id, user_id, first_seen_time, last_seen_user_name, last_seen_time, last_seen_address, last_seen_hwid
                FROM player
                WHERE last_seen_user_name = $1
            """, user_name)

            if result:
                last_seen_address = result['last_seen_address']
                last_seen_hwid = result['last_seen_hwid']
                related = await conn.fetch("""
                    SELECT last_seen_user_name, last_seen_address, last_seen_hwid, last_seen_time
                    FROM player
                    WHERE last_seen_address = $1 OR last_seen_hwid = $2
                """, last_seen_address, last_seen_hwid)
            else:
                related = []

            return result, related
        finally:
            await conn.close()

    async def add_permission_admin(self, guid: str, username: str, title: str, permission: str, db_name: str = 'astra'):
        conn = await self.get_connection(db_name)
        try:
            async with conn.transaction():

                rank_id = await conn.fetchval("SELECT admin_rank_id FROM admin_rank WHERE name ILIKE $1", permission)
                if not rank_id:
                    return False, f"Не найден ранг с названием {permission}"

                await conn.execute("""
                    INSERT INTO admin (user_id, title, admin_rank_id)
                    VALUES ($1, $2, $3)
                """, guid, title, rank_id)

                return True, f"Права были успешно добавлены для {username} в БД {db_name.upper()}"

        except Exception as e:
            return False, f"Ошибка: {e}"
        finally:
            await conn.close()

    async def del_permission_admin(self, guid: str, username: str, db_name: str = 'astra'):
        conn = await self.get_connection(db_name)
        try:
            async with conn.transaction():

                await conn.execute("""
                    DELETE FROM admin WHERE user_id = $1""", guid)

                return True, f"Права были успешно сняты для {username} в БД {db_name.upper()}"

        except Exception as e:
            return False, f"Ошибка: {e}"
        finally:
            await conn.close()
        
    async def tweak_permission_admin(self, guid: str, username: str, title: str, permission: str, db_name: str = 'astra'):
        conn = await self.get_connection(db_name)
        try:
            async with conn.transaction():

                rank_id = await conn.fetchval("SELECT admin_rank_id FROM admin_rank WHERE name ILIKE $1", permission)
                if not rank_id:
                    return False, f"Не найден ранг с названием {permission}"

                await conn.execute("""
                    UPDATE admin SET title = $1, admin_rank_id = $2 WHERE user_id = $3
                """, title, rank_id, guid)

                return True, f"Права были успешно изменены для {username} в БД {db_name.upper()}"
        except Exception as e:
            return False, f"Ошибка: {e}"
        finally:
            await conn.close()

    async def is_linked(self, discord_id: str, db_name: str = 'astra'):
        last_error = None
        for current_db in self._linked_lookup_order(db_name):
            conn = None
            try:
                conn = await self.get_connection(current_db)
                result = await conn.fetchval("SELECT 1 FROM discord_user WHERE discord_id = $1", discord_id)
                if result:
                    return True
            except Exception as e:
                last_error = e
            finally:
                if conn:
                    await conn.close()
        if last_error:
            print(f"Ошибка проверки привязки discord_id={discord_id}: {last_error}")
        return False

    async def get_all_linked_discord_ids(self, db_name: str = 'astra') -> set[str]:
        target_dbs = self._linked_lookup_order(db_name)
        if not target_dbs:
            return set()

        async def _fetch_from_db(db_key: str) -> tuple[str, set[str], Exception | None]:
            conn = None
            try:
                conn = await self.get_connection(db_key)
                rows = await conn.fetch("SELECT DISTINCT discord_id FROM discord_user WHERE discord_id IS NOT NULL")
                ids = {str(row["discord_id"]) for row in rows if row["discord_id"]}
                return db_key, ids, None
            except Exception as e:
                return db_key, set(), e
            finally:
                if conn:
                    await conn.close()

        tasks = [_fetch_from_db(db_key) for db_key in target_dbs]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        linked_ids: set[str] = set()
        errors: list[str] = []
        for db_key, ids, err in results:
            linked_ids.update(ids)
            if err:
                errors.append(f"{db_key.upper()}: {err}")

        if errors and not linked_ids:
            print(f"Ошибка получения списка привязок: {'; '.join(errors)}")

        return linked_ids

    @staticmethod
    def _normalize_link_code(link_code: str | None) -> str:
        if link_code is None:
            return ""
        return link_code.strip().upper()

    async def _ensure_link_code_table(self, conn: asyncpg.Connection) -> None:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS discord_link_code (
                user_id TEXT PRIMARY KEY,
                code TEXT NOT NULL UNIQUE,
                expires_at BIGINT NOT NULL
            )
        """)

        schema_type = await conn.fetchval("""
            SELECT data_type
            FROM information_schema.columns
            WHERE table_name = 'discord_link_code'
              AND column_name = 'expires_at'
            LIMIT 1
        """)

        if schema_type and "int" not in str(schema_type).lower():
            await conn.execute("DROP TABLE IF EXISTS discord_link_code")
            await conn.execute("""
                CREATE TABLE discord_link_code (
                    user_id TEXT PRIMARY KEY,
                    code TEXT NOT NULL UNIQUE,
                    expires_at BIGINT NOT NULL
                )
            """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS ix_discord_link_code_expires_at
            ON discord_link_code (expires_at)
        """)

    async def _find_guid_by_link_code_in_db(self, link_code: str, db_name: str) -> str | None:
        conn = await self.get_connection(db_name)
        try:
            await self._ensure_link_code_table(conn)
            now_unix = int(datetime.utcnow().timestamp())
            await conn.execute("DELETE FROM discord_link_code WHERE expires_at <= $1", now_unix)
            result = await conn.fetchval(
                "SELECT user_id FROM discord_link_code WHERE code = $1 AND expires_at > $2 LIMIT 1",
                link_code,
                now_unix
            )
            return str(result) if result else None
        finally:
            await conn.close()

    async def _delete_link_code_in_db(self, link_code: str, db_name: str) -> tuple[bool, str]:
        conn = await self.get_connection(db_name)
        try:
            await self._ensure_link_code_table(conn)
            await conn.execute("DELETE FROM discord_link_code WHERE code = $1", link_code)
            return True, "deleted"
        except Exception as e:
            return False, str(e)
        finally:
            await conn.close()

    async def _claim_link_code_in_db(
        self,
        link_code: str,
        db_name: str
    ) -> tuple[bool, str | None, int | None, str]:
        """
        Атомарно «поглощает» код (delete-returning) и возвращает GUID + expires_at.
        Если код уже использован/просрочен, вернет (True, None, None, "not_found").
        """
        conn = None
        try:
            conn = await self.get_connection(db_name)
            async with conn.transaction():
                await self._ensure_link_code_table(conn)
                now_unix = int(datetime.utcnow().timestamp())
                await conn.execute("DELETE FROM discord_link_code WHERE expires_at <= $1", now_unix)
                row = await conn.fetchrow(
                    """
                    DELETE FROM discord_link_code
                    WHERE code = $1 AND expires_at > $2
                    RETURNING user_id, expires_at
                    """,
                    link_code,
                    now_unix
                )

                if not row:
                    return True, None, None, "not_found"

                return True, str(row["user_id"]), int(row["expires_at"]), "claimed"
        except Exception as e:
            return False, None, None, str(e)
        finally:
            if conn:
                await conn.close()

    async def _restore_link_code_in_db(
        self,
        user_id: str,
        link_code: str,
        expires_at: int,
        db_name: str
    ) -> tuple[bool, str]:
        """
        Восстанавливает ранее atomically-claimed код, если привязка не завершилась.
        """
        conn = None
        try:
            conn = await self.get_connection(db_name)
            async with conn.transaction():
                await self._ensure_link_code_table(conn)
                await conn.execute(
                    """
                    INSERT INTO discord_link_code (user_id, code, expires_at)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (user_id)
                    DO UPDATE SET code = EXCLUDED.code, expires_at = EXCLUDED.expires_at
                    """,
                    user_id,
                    link_code,
                    expires_at
                )
            return True, "restored"
        except Exception as e:
            return False, str(e)
        finally:
            if conn:
                await conn.close()

    async def consume_link_code(self, link_code: str, db_name: str = 'astra') -> tuple[bool, str]:
        code = self._normalize_link_code(link_code)
        if not LINK_CODE_REGEX.fullmatch(code):
            return False, "Неверный формат кода."

        target_dbs = self._linked_lookup_order(db_name)
        if not target_dbs:
            return False, "Нет настроенных БД для удаления кода."

        errors: list[str] = []
        for current_db in target_dbs:
            ok, message = await self._delete_link_code_in_db(code, current_db)
            if not ok:
                errors.append(f"{current_db.upper()}: {message}")

        if errors:
            return False, f"Код удален частично: {'; '.join(errors)}"

        return True, "Код удален."

    async def link_user_by_code(self, link_code: str, discord_id: str, db_name: str = 'astra') -> tuple[bool, str]:
        code = self._normalize_link_code(link_code)
        if not LINK_CODE_REGEX.fullmatch(code):
            return False, "Неверный формат кода. Ожидается 9 HEX-символов."

        target_dbs = self._linked_lookup_order(db_name)
        if not target_dbs:
            return False, "Нет настроенных БД для привязки."

        guid: str | None = None
        source_db: str | None = None
        code_expires_at: int | None = None
        errors: list[str] = []

        for current_db in target_dbs:
            ok, claimed_guid, expires_at, message = await self._claim_link_code_in_db(code, current_db)
            if not ok:
                errors.append(f"{current_db.upper()}: {message}")
                continue

            if claimed_guid:
                guid = claimed_guid
                source_db = current_db
                code_expires_at = expires_at
                break

        if not guid:
            if errors:
                print(f"Ошибка поиска GUID по коду {code}: {'; '.join(errors)}")
            return False, "Код недействителен или истек."

        success, message = await self.link_user(guid, discord_id, source_db or db_name)
        if not success and source_db and code_expires_at is not None:
            restore_ok, restore_message = await self._restore_link_code_in_db(
                guid,
                code,
                code_expires_at,
                source_db
            )
            if not restore_ok:
                message = f"{message} Не удалось восстановить код привязки: {restore_message}."

        return success, message

    async def _insert_link_in_db(self, guid: str, discord_id: str, db_name: str) -> tuple[bool, bool, str]:
        conn = None
        try:
            conn = await self.get_connection(db_name)
            async with conn.transaction():
                existing_guid = await conn.fetchval(
                    "SELECT user_id FROM discord_user WHERE discord_id = $1",
                    discord_id
                )
                if existing_guid:
                    if str(existing_guid) == str(guid):
                        return True, False, "already_linked"
                    return False, False, f"discord_id уже привязан к другому GUID ({existing_guid}) в БД {db_name.upper()}"

                max_id = await conn.fetchval("SELECT COALESCE(MAX(discord_user_id), 0) FROM discord_user") or 0
                next_id = max_id + 1
                await conn.execute(
                    "INSERT INTO discord_user (discord_user_id, user_id, discord_id) VALUES ($1, $2, $3)",
                    next_id,
                    guid,
                    discord_id
                )
                return True, True, "inserted"
        except Exception as e:
            return False, False, str(e)
        finally:
            if conn:
                await conn.close()

    async def _delete_link_in_db(self, discord_id: str, db_name: str) -> tuple[bool, bool, str]:
        conn = None
        try:
            conn = await self.get_connection(db_name)
            async with conn.transaction():
                deleted = await conn.fetchval(
                    "DELETE FROM discord_user WHERE discord_id = $1 RETURNING user_id",
                    discord_id
                )
                return True, bool(deleted), "deleted" if deleted else "not_found"
        except Exception as e:
            return False, False, str(e)
        finally:
            if conn:
                await conn.close()

    async def _delete_link_by_user_id_in_db(self, user_id: str, db_name: str) -> tuple[bool, bool, str, str | None]:
        conn = None
        try:
            conn = await self.get_connection(db_name)
            async with conn.transaction():
                row = await conn.fetchrow(
                    "DELETE FROM discord_user WHERE user_id = $1 RETURNING discord_id",
                    user_id
                )
                if row and row["discord_id"]:
                    return True, True, "deleted", str(row["discord_id"])

                return True, False, "not_found", None
        except Exception as e:
            return False, False, str(e), None
        finally:
            if conn:
                await conn.close()

    async def link_user(self, guid: str, discord_id: str, db_name: str = 'astra'):
        target_dbs = self._linked_lookup_order(db_name)
        if not target_dbs:
            return False, "Нет настроенных БД для привязки."
        inserted_dbs: list[str] = []
        already_linked_dbs: list[str] = []

        for current_db in target_dbs:
            ok, inserted, message = await self._insert_link_in_db(guid, discord_id, current_db)
            if not ok:
                rollback_errors: list[str] = []
                for rollback_db in inserted_dbs:
                    rb_ok, _, rb_message = await self._delete_link_in_db(discord_id, rollback_db)
                    if not rb_ok:
                        rollback_errors.append(f"{rollback_db.upper()}: {rb_message}")

                rollback_suffix = ""
                if rollback_errors:
                    rollback_suffix = f" Откат выполнен с ошибками: {'; '.join(rollback_errors)}"

                return False, f"Ошибка привязки {current_db.upper()}: {message}.{rollback_suffix}"

            if inserted:
                inserted_dbs.append(current_db)
            elif message == "already_linked":
                already_linked_dbs.append(current_db)

        if not inserted_dbs and len(already_linked_dbs) == len(target_dbs):
            return False, "Аккаунт уже привязан во всех доступных БД."

        return True, "Аккаунт привязан."

    async def unlink_user(self, discord_id: str, db_name: str = 'astra') -> tuple[bool, str]:
        target_dbs = self._linked_lookup_order(db_name)
        if not target_dbs:
            return False, "Нет настроенных БД для отвязки."
        deleted_any = False
        errors: list[str] = []

        for current_db in target_dbs:
            ok, deleted, message = await self._delete_link_in_db(discord_id, current_db)
            if not ok:
                errors.append(f"{current_db.upper()}: {message}")
                continue
            if deleted:
                deleted_any = True

        if errors and not deleted_any:
            return False, f"Ошибка отвязки: {'; '.join(errors)}"

        if errors and deleted_any:
            return False, f"Частичная отвязка (есть ошибки): {'; '.join(errors)}"

        if deleted_any:
            return True, f"Аккаунт отвязан."

        return False, "Аккаунт не привязан."

    async def unlink_user_global(
        self,
        user_id: str | None = None,
        discord_id: str | None = None,
        db_name: str = "astra"
    ) -> tuple[bool, str, str | None]:
        normalized_user_id = (user_id or "").strip()
        normalized_discord_id = (discord_id or "").strip()

        if not normalized_user_id and not normalized_discord_id:
            return False, "Не указан user_id или discord_id.", None

        target_dbs = self._linked_lookup_order(db_name)
        if not target_dbs:
            return False, "Нет настроенных БД для отвязки.", None

        resolved_discord_id = normalized_discord_id or None
        deleted_any = False
        errors: list[str] = []

        if normalized_user_id:
            for current_db in target_dbs:
                ok, deleted, message, deleted_discord_id = await self._delete_link_by_user_id_in_db(
                    normalized_user_id,
                    current_db
                )
                if not ok:
                    errors.append(f"{current_db.upper()}: {message}")
                    continue

                if deleted:
                    deleted_any = True
                    if deleted_discord_id and resolved_discord_id is None:
                        resolved_discord_id = deleted_discord_id

        # Дополнительный проход по discord_id для полной очистки конфликтных хвостов.
        if normalized_discord_id:
            for current_db in target_dbs:
                ok, deleted, message = await self._delete_link_in_db(normalized_discord_id, current_db)
                if not ok:
                    errors.append(f"{current_db.upper()}: {message}")
                    continue
                if deleted:
                    deleted_any = True

        if errors and not deleted_any:
            return False, f"Ошибка отвязки: {'; '.join(errors)}", resolved_discord_id

        if errors and deleted_any:
            return False, f"Частичная отвязка (есть ошибки): {'; '.join(errors)}", resolved_discord_id

        if deleted_any:
            return True, "Аккаунт отвязан.", resolved_discord_id

        return False, "Аккаунт не привязан.", resolved_discord_id

    async def get_logs_by_round(self, username: str, round_id: int, db_name: str = 'astra'):
        conn = await self.get_connection(db_name)
        try:
            keywords = ["used placement system to create", "Дебаг", "Админ", "was respawned", "Трюки", "Покарать"]

            like_username = f"%{username}%"
            or_conditions = " OR ".join(f"message ILIKE '%{kw}%'" for kw in keywords)
            query = f"SELECT message FROM admin_log WHERE round_id = $1 AND message ILIKE $2 AND ({or_conditions})"
            
            results = await conn.fetch(query, round_id, like_username)
            return results
        finally:
            await conn.close()

    async def get_list_permission(self, db_name: str = 'astra'):
        conn = await self.get_connection(db_name)
        try:
            result = await conn.fetch("SELECT name FROM admin_rank ORDER BY admin_rank_id ASC")
            return result
        finally:
            await conn.close()



