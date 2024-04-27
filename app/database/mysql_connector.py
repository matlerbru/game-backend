from mysql.connector.aio import connect
from mysql.connector.errors import InterfaceError, ProgrammingError
from database.interface import CursorInterface
from mysql.connector.abstracts import MySQLCursorAbstract
from typing import Self
import asyncio


class MySqlConnection:

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        name: str,
        semaphore: asyncio.Semaphore,
    ) -> None:
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._name = name
        self._connection = None
        self._semaphore = semaphore

    async def connect(self) -> None:
        self._connection = await connect(
            user=self._user,
            password=self._password,
            host=self._host,
            database=self._name,
            port=self._port,
        )

    @classmethod
    async def async_connect(
        cls,
        host: str,
        port: int,
        user: str,
        password: str,
        name: str,
        semaphore: asyncio.Semaphore,
    ) -> Self:
        c = cls(host, port, user, password, name, semaphore)
        await c.connect()
        return c

    async def cursor(self):
        cursor = await self._connection.cursor(dictionary=True, buffered=True)
        return self._Cursor(cursor)

    async def close(self) -> None:
        await self._connection.close()
        self._semaphore.release()

    async def commit(self) -> None:
        await self._connection.commit()

    async def rollback(self) -> None:
        await self._connection.rollback()

    @staticmethod
    async def is_connectable(
        host: str, port: int, user: str, password: str, name: str
    ) -> bool:
        try:
            await MySqlConnection.async_connect(host, port, user, password, name, 1)
            return True
        except Exception:
            return False

    class ConnectionError(Exception):
        pass

    class DuplicateEntryError(Exception):
        pass

    class _Cursor(CursorInterface):

        def __init__(
            self,
            cursor: MySQLCursorAbstract,
        ) -> None:
            self._cursor = cursor

        async def execute(
            self, query: str, args: list[str | int | float | bool] | None = None
        ) -> list[dict[str, str | int | float | bool]]:
            if args and not query.count("%s") == len(args):
                raise KeyError(
                    "Argument list is different length than query argument count"
                )

            try:
                await self._cursor.execute(query, args)
                try:
                    return await self._cursor.fetchall()
                except InterfaceError:
                    return []
            except ProgrammingError:
                raise self.CursorNotConnectedError

        async def execute_multiple(
            self, queries: str, args: list[str | int | float | bool] | None = None
        ) -> list[dict[str, str | int | float | bool]]:

            if args and not queries.count("%s") == len(args):
                raise KeyError(
                    "Argument list is different length than query argument count"
                )

            results = []
            for q in [f"{q};".strip() for q in queries.split(";") if q.strip()]:
                if not (q.endswith(";")):
                    break

                try:
                    await self._cursor.execute(
                        q, [args.pop(0) for _ in range(q.count("%s"))]
                    )

                    r = []

                    while res := await self._cursor.fetchone():
                        r.append(res)
                    results.append(r)
                except ProgrammingError:
                    raise self.CursorNotConnectedError

            return results

        async def execute_file(self, file: str) -> dict[str | int | float | bool]:
            with open(file) as file:
                query = "".join(file.readlines())
                return await self.execute_multiple(query)

        async def close(self) -> None:
            await self._cursor.close()


class ConnectionSemaphore:

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        name: str,
        connection_limit: int,
    ) -> None:
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._name = name
        self._semaphore = asyncio.Semaphore(connection_limit)

    async def acquire(self) -> MySqlConnection:
        await self._semaphore.acquire()

        return await MySqlConnection.async_connect(
            self._host,
            self._port,
            self._user,
            self._password,
            self._name,
            self._semaphore,
        )


async def acquire_database_connection(connection_semaphore: ConnectionSemaphore):
    connection = await connection_semaphore.acquire()
    return connection
