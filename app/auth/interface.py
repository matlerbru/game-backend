from abc import ABC, abstractmethod
import schemas
from fastapi import Depends
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from abc import ABC, abstractmethod

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


class AuthorizationServiceInterface(ABC):

    @abstractmethod
    def __init__(
        self,
        signing: str,
        hash_key: str,
        token_expiration_time: int,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def authenticate_user(self, user: str | int, password: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def hash_password(self, password: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def authenticate(
        self, token: Annotated[str, Depends(oauth2_scheme)]
    ) -> schemas.UserAuth:
        raise NotImplementedError

    class InvalidTokenError(Exception):
        pass

    class InvalidCredentialsError(Exception):
        pass

    class InvalidPasswordError(Exception):
        pass
