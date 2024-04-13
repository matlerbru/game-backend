import schemas
from abc import ABC, abstractmethod
from auth.interface import AuthorizationServiceInterface


class UserServiceInterface:

    @abstractmethod
    def __init__(self, auth: AuthorizationServiceInterface) -> None:
        raise NotImplementedError

    @abstractmethod
    async def create_user(self, username: str, password: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def remove_user(self, username: str, password: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_user(self, username: str) -> schemas.User:
        raise NotImplementedError

    @abstractmethod
    async def set_variable(self, user_id: int, key: str, value: str | None) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_variable(
        self,
        user_id: int,
        key: str,
    ) -> str:
        pass

    @abstractmethod
    async def change_password(self, user: str | int, password: str) -> None:
        raise NotImplementedError

    class KeyNotExistingError(Exception):
        pass

    class DuplicateUserError(Exception):
        pass

    class UserNotExistingError(Exception):
        pass

    class UserNotDeletedError(Exception):
        pass
