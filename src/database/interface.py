from mysql.connector.abstracts import MySQLCursorAbstract
from abc import ABC, abstractmethod
from typing import Self
import asyncio


class CursorInterface(ABC):

    @abstractmethod
    def __init__(
        self,
        cursor: MySQLCursorAbstract,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def execute(
        self, query: str, args: list[str | int | float | bool] | None = None
    ) -> dict[str, str | int | float | bool]:
        raise NotImplementedError

    @abstractmethod
    async def execute_multiple(
        self, queries: str, args: list[str | int | float | bool] | None = None
    ) -> list[dict[str, str | int | float | bool]]:
        raise NotImplementedError

    @abstractmethod
    async def execute_file(self, file: str) -> dict[str | int | float | bool]:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError
    
    class CursorNotConnectedError(Exception):
        pass


class MySqlConnection(ABC):

    @abstractmethod
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        name: str,
        semaphore: asyncio.Semaphore,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def connect(self) -> None:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    async def async_connect(
        cls,
        host: str,
        port: int,
        user: str,
        password: str,
        name: str,
        semaphore: asyncio.Semaphore,
    ) -> Self:
        raise NotImplementedError

    @abstractmethod
    async def cursor(self) -> CursorInterface:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def is_connectable() -> bool:
        raise NotImplementedError

    class ConnectionError(Exception):
        pass

    class DuplicateEntryError(Exception):
        pass


class ConnectionSemaphore(ABC):

    @abstractmethod
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        name: str,
        connection_limit: int,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def acquire(self):
        raise NotImplementedError
